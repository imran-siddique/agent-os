/**
 * Copilot Extension Handler
 * 
 * Main handler for GitHub Copilot Extension interactions.
 * Filters suggestions, handles chat commands, and provides annotations.
 */

import { PolicyEngine, AnalysisResult } from './policyEngine';
import { CMVKClient, CMVKResult } from './cmvkClient';
import { AuditLogger } from './auditLogger';
import { logger } from './logger';

export interface CopilotSuggestion {
    id: string;
    code: string;
    language: string;
    confidence: number;
    metadata?: Record<string, any>;
}

export interface CopilotContext {
    file?: {
        path: string;
        language: string;
        content?: string;
    };
    selection?: {
        start: { line: number; column: number };
        end: { line: number; column: number };
        text: string;
    };
    user?: {
        id: string;
        organization?: string;
    };
    repository?: {
        name: string;
        owner: string;
    };
}

export interface FilteredSuggestion extends CopilotSuggestion {
    safetyStatus: 'safe' | 'warning' | 'blocked';
    safetyMessage?: string;
    annotations?: SafetyAnnotation[];
}

export interface SafetyAnnotation {
    line: number;
    column: number;
    endLine?: number;
    endColumn?: number;
    severity: 'error' | 'warning' | 'info';
    message: string;
    rule: string;
    suggestion?: string;
}

export interface ChatResponse {
    message: string;
    markdown: boolean;
    suggestions?: string[];
    actions?: ChatAction[];
}

export interface ChatAction {
    label: string;
    command: string;
    args?: any;
}

export class CopilotExtension {
    constructor(
        private policyEngine: PolicyEngine,
        private cmvkClient: CMVKClient,
        private auditLogger: AuditLogger
    ) {}

    /**
     * Filter Copilot suggestions for safety
     */
    async filterSuggestions(
        suggestions: CopilotSuggestion[],
        context: CopilotContext
    ): Promise<{ suggestions: FilteredSuggestion[]; summary: FilterSummary }> {
        const filteredSuggestions: FilteredSuggestion[] = [];
        let blocked = 0;
        let warnings = 0;
        let safe = 0;

        for (const suggestion of suggestions) {
            const language = suggestion.language || context.file?.language || 'unknown';
            const result = await this.policyEngine.analyzeCode(suggestion.code, language);

            const filtered: FilteredSuggestion = {
                ...suggestion,
                safetyStatus: 'safe',
                annotations: []
            };

            if (result.blocked) {
                filtered.safetyStatus = 'blocked';
                filtered.safetyMessage = result.reason;
                filtered.annotations = this.createAnnotations(suggestion.code, result);
                blocked++;

                // Log violation
                this.auditLogger.log({
                    type: 'blocked',
                    timestamp: new Date(),
                    file: context.file?.path,
                    language,
                    code: suggestion.code.substring(0, 200),
                    violation: result.violation,
                    reason: result.reason,
                    repository: context.repository ? 
                        `${context.repository.owner}/${context.repository.name}` : undefined
                });

            } else if (result.warnings.length > 0) {
                filtered.safetyStatus = 'warning';
                filtered.safetyMessage = result.warnings.join('; ');
                filtered.annotations = this.createWarningAnnotations(suggestion.code, result.warnings);
                warnings++;

            } else {
                safe++;
            }

            filteredSuggestions.push(filtered);
        }

        const summary: FilterSummary = {
            total: suggestions.length,
            safe,
            warnings,
            blocked,
            timestamp: new Date().toISOString()
        };

        logger.info('Suggestions filtered', summary);

        return { suggestions: filteredSuggestions, summary };
    }

    /**
     * Handle @agent-os chat commands
     */
    async handleChatMessage(
        message: string,
        context: CopilotContext,
        command?: string
    ): Promise<ChatResponse> {
        // Parse command from message if not provided
        if (!command && message.startsWith('@agent-os')) {
            const parts = message.replace('@agent-os', '').trim().split(' ');
            command = parts[0];
            message = parts.slice(1).join(' ');
        }

        switch (command?.toLowerCase()) {
            case 'review':
                return this.handleReviewCommand(message, context);
            
            case 'policy':
                return this.handlePolicyCommand(message, context);
            
            case 'audit':
                return this.handleAuditCommand(context);
            
            case 'help':
            default:
                return this.handleHelpCommand();
        }
    }

    /**
     * @agent-os review - Review code with CMVK
     */
    private async handleReviewCommand(
        message: string,
        context: CopilotContext
    ): Promise<ChatResponse> {
        const code = context.selection?.text || message || context.file?.content;
        
        if (!code || code.trim().length === 0) {
            return {
                message: '⚠️ No code to review. Please select code or provide it in your message.',
                markdown: false
            };
        }

        const language = context.file?.language || 'unknown';

        // First, run local policy check
        const policyResult = await this.policyEngine.analyzeCode(code, language);
        
        // Then, run CMVK verification
        let cmvkResult: CMVKResult | null = null;
        try {
            cmvkResult = await this.cmvkClient.reviewCode(code, language);
        } catch (error) {
            logger.warn('CMVK review failed, using local analysis only', { error });
        }

        // Build response
        let response = '# 🛡️ Agent OS Code Review\n\n';

        // Policy results
        if (policyResult.blocked) {
            response += `## ❌ Policy Violation\n`;
            response += `**${policyResult.reason}**\n\n`;
            if (policyResult.suggestion) {
                response += `💡 **Suggestion:** ${policyResult.suggestion}\n\n`;
            }
        } else if (policyResult.warnings.length > 0) {
            response += `## ⚠️ Policy Warnings\n`;
            for (const warning of policyResult.warnings) {
                response += `- ${warning}\n`;
            }
            response += '\n';
        } else {
            response += `## ✅ Policy Check Passed\n\n`;
        }

        // CMVK results
        if (cmvkResult) {
            const consensusEmoji = cmvkResult.consensus >= 0.8 ? '✅' : 
                                   cmvkResult.consensus >= 0.5 ? '⚠️' : '❌';
            
            response += `## ${consensusEmoji} CMVK Multi-Model Review\n\n`;
            response += `**Consensus:** ${(cmvkResult.consensus * 100).toFixed(0)}%\n\n`;
            
            response += '| Model | Status | Assessment |\n';
            response += '|-------|--------|------------|\n';
            
            for (const result of cmvkResult.modelResults) {
                const status = result.passed ? '✅' : '⚠️';
                response += `| ${result.model} | ${status} | ${result.summary} |\n`;
            }
            response += '\n';

            if (cmvkResult.issues.length > 0) {
                response += `### Issues Found\n`;
                for (const issue of cmvkResult.issues) {
                    response += `- ${issue}\n`;
                }
                response += '\n';
            }

            if (cmvkResult.recommendations) {
                response += `### Recommendations\n${cmvkResult.recommendations}\n`;
            }
        }

        // Log review
        this.auditLogger.log({
            type: 'cmvk_review',
            timestamp: new Date(),
            file: context.file?.path,
            language,
            code: code.substring(0, 200),
            result: {
                policyBlocked: policyResult.blocked,
                cmvkConsensus: cmvkResult?.consensus
            }
        });

        return {
            message: response,
            markdown: true,
            actions: policyResult.blocked ? [
                { label: 'Show Policy', command: 'agent-os.policy' },
                { label: 'Allow Once', command: 'agent-os.allowOnce', args: { violation: policyResult.violation } }
            ] : undefined
        };
    }

    /**
     * @agent-os policy - Show or configure policies
     */
    private handlePolicyCommand(message: string, context: CopilotContext): ChatResponse {
        const policies = this.policyEngine.getActivePolicies();
        
        let response = '# 🛡️ Agent OS Active Policies\n\n';
        response += '| Policy | Status | Severity |\n';
        response += '|--------|--------|----------|\n';
        
        for (const policy of policies) {
            const status = policy.enabled ? '✅ Enabled' : '❌ Disabled';
            response += `| ${policy.name} | ${status} | ${policy.severity} |\n`;
        }

        response += '\n---\n';
        response += `📊 **Total Rules:** ${this.policyEngine.getRuleCount()}\n\n`;
        response += 'To configure policies, edit `.github/agent-os.json` or your repository settings.\n';

        return {
            message: response,
            markdown: true,
            suggestions: [
                '@agent-os review - Review selected code',
                '@agent-os audit - View recent audit log'
            ]
        };
    }

    /**
     * @agent-os audit - Show recent audit log
     */
    private handleAuditCommand(context: CopilotContext): ChatResponse {
        const logs = this.auditLogger.getRecent(10);
        const stats = this.auditLogger.getStats();
        
        let response = '# 📋 Agent OS Audit Log\n\n';
        
        response += '## Summary\n';
        response += `- **Blocked Today:** ${stats.blockedToday}\n`;
        response += `- **Blocked This Week:** ${stats.blockedThisWeek}\n`;
        response += `- **CMVK Reviews:** ${stats.cmvkReviewsToday}\n\n`;

        if (logs.length > 0) {
            response += '## Recent Activity\n\n';
            response += '| Time | Type | Details |\n';
            response += '|------|------|--------|\n';
            
            for (const log of logs) {
                const time = this.formatTime(log.timestamp);
                const type = log.type === 'blocked' ? '🚫 Blocked' : 
                            log.type === 'cmvk_review' ? '🔍 Review' : '⚠️ Warning';
                const details = log.violation || log.reason || 'N/A';
                response += `| ${time} | ${type} | ${details.substring(0, 30)}... |\n`;
            }
        } else {
            response += '*No recent activity*\n';
        }

        return {
            message: response,
            markdown: true
        };
    }

    /**
     * @agent-os help - Show help
     */
    private handleHelpCommand(): ChatResponse {
        const response = `# 🛡️ Agent OS for Copilot

**Available Commands:**

| Command | Description |
|---------|-------------|
| \`@agent-os review\` | Review selected code with CMVK multi-model verification |
| \`@agent-os policy\` | Show active safety policies |
| \`@agent-os audit\` | View recent safety audit log |
| \`@agent-os help\` | Show this help message |

**What Agent OS Does:**
- 🔒 Automatically filters dangerous Copilot suggestions
- 🔍 Verifies code with multiple AI models (CMVK)
- 📋 Maintains audit trail of all AI interactions
- 🛡️ Enforces security policies (no secrets, no destructive ops)

**Learn More:** [github.com/imran-siddique/agent-os](https://github.com/imran-siddique/agent-os)
`;

        return {
            message: response,
            markdown: true,
            suggestions: [
                '@agent-os review',
                '@agent-os policy',
                '@agent-os audit'
            ]
        };
    }

    /**
     * Annotate code with safety markers
     */
    async annotateCode(
        code: string,
        language: string,
        context: CopilotContext
    ): Promise<SafetyAnnotation[]> {
        const result = await this.policyEngine.analyzeCode(code, language);
        return this.createAnnotations(code, result);
    }

    /**
     * Create annotations from analysis result
     */
    private createAnnotations(code: string, result: AnalysisResult): SafetyAnnotation[] {
        const annotations: SafetyAnnotation[] = [];
        
        if (result.blocked) {
            // Find the line containing the violation (simple heuristic)
            const lines = code.split('\n');
            for (let i = 0; i < lines.length; i++) {
                // Match against common dangerous patterns
                if (this.lineMatchesViolation(lines[i], result.violation)) {
                    annotations.push({
                        line: i + 1,
                        column: 1,
                        severity: 'error',
                        message: result.reason,
                        rule: result.violation,
                        suggestion: result.suggestion
                    });
                    break;
                }
            }

            // If no specific line found, annotate first line
            if (annotations.length === 0) {
                annotations.push({
                    line: 1,
                    column: 1,
                    severity: 'error',
                    message: result.reason,
                    rule: result.violation,
                    suggestion: result.suggestion
                });
            }
        }

        return annotations;
    }

    /**
     * Create warning annotations
     */
    private createWarningAnnotations(code: string, warnings: string[]): SafetyAnnotation[] {
        return warnings.map((warning, index) => ({
            line: 1,
            column: 1,
            severity: 'warning' as const,
            message: warning,
            rule: `warning_${index}`
        }));
    }

    /**
     * Check if line matches violation pattern
     */
    private lineMatchesViolation(line: string, violation: string): boolean {
        const patterns: Record<string, RegExp> = {
            'drop_table': /DROP\s+TABLE/i,
            'delete_all': /DELETE\s+FROM/i,
            'rm_rf': /rm\s+-rf/i,
            'hardcoded_api_key': /api[_-]?key\s*=/i,
            'hardcoded_password': /password\s*=/i,
            'sudo': /sudo\s+/i,
            'chmod_777': /chmod\s+777/i
        };

        const pattern = patterns[violation];
        return pattern ? pattern.test(line) : false;
    }

    /**
     * Format timestamp for display
     */
    private formatTime(timestamp: Date): string {
        const now = new Date();
        const diff = now.getTime() - new Date(timestamp).getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);

        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return new Date(timestamp).toLocaleDateString();
    }
}

interface FilterSummary {
    total: number;
    safe: number;
    warnings: number;
    blocked: number;
    timestamp: string;
}
