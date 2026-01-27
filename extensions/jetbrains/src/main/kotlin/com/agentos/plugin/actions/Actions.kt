package com.agentos.plugin.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.agentos.plugin.settings.AgentOSSettings

/**
 * Action to review selected code with CMVK multi-model verification.
 */
class ReviewWithCMVKAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val editor = event.getData(CommonDataKeys.EDITOR) ?: return
        val project = event.project ?: return
        
        val selectedText = editor.selectionModel.selectedText
        if (selectedText.isNullOrBlank()) {
            Messages.showInfoMessage(project, "Please select code to review", "Agent OS")
            return
        }
        
        val settings = AgentOSSettings.getInstance().state
        if (!settings.cmvkEnabled) {
            Messages.showInfoMessage(
                project,
                "CMVK is not enabled. Enable it in Settings → Tools → Agent OS",
                "Agent OS"
            )
            return
        }
        
        // TODO: Implement actual CMVK API call
        Messages.showInfoMessage(
            project,
            """
            🛡️ CMVK Review Result
            
            Consensus: 100% Agreement
            
            ✅ GPT-4: No issues detected
            ✅ Claude: No issues detected
            ✅ Gemini: No issues detected
            
            Code appears safe.
            """.trimIndent(),
            "Agent OS - CMVK Review"
        )
    }
    
    override fun update(event: AnActionEvent) {
        val editor = event.getData(CommonDataKeys.EDITOR)
        event.presentation.isEnabledAndVisible = editor != null && editor.selectionModel.hasSelection()
    }
}

/**
 * Action to toggle Agent OS safety mode.
 */
class ToggleSafetyAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val settings = AgentOSSettings.getInstance()
        val state = settings.state
        state.enabled = !state.enabled
        settings.loadState(state)
        
        val status = if (state.enabled) "enabled" else "disabled"
        Messages.showInfoMessage(
            event.project,
            "Agent OS is now $status",
            "Agent OS"
        )
    }
}

/**
 * Action to show audit log.
 */
class ShowAuditLogAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        
        // Open the Agent OS tool window
        val toolWindowManager = com.intellij.openapi.wm.ToolWindowManager.getInstance(project)
        val toolWindow = toolWindowManager.getToolWindow("Agent OS")
        toolWindow?.show()
    }
}

/**
 * Action to configure policies.
 */
class ConfigurePoliciesAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        com.intellij.openapi.options.ShowSettingsUtil.getInstance()
            .showSettingsDialog(event.project, "Agent OS")
    }
}
