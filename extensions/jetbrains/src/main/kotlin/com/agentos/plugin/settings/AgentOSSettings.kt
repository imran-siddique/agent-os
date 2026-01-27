package com.agentos.plugin.settings

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage

/**
 * Persistent settings for Agent OS plugin.
 */
@State(
    name = "AgentOSSettings",
    storages = [Storage("AgentOSSettings.xml")]
)
class AgentOSSettings : PersistentStateComponent<AgentOSSettings.State> {
    
    data class State(
        var enabled: Boolean = true,
        var mode: String = "basic",  // basic, enhanced, enterprise
        
        // Policies
        var blockDestructiveSQL: Boolean = true,
        var blockFileDeletes: Boolean = true,
        var blockSecretExposure: Boolean = true,
        var blockPrivilegeEscalation: Boolean = true,
        var blockUnsafeNetworkCalls: Boolean = false,
        
        // CMVK
        var cmvkEnabled: Boolean = false,
        var cmvkModels: List<String> = listOf("gpt-4", "claude-sonnet-4", "gemini-pro"),
        var cmvkConsensusThreshold: Double = 0.8,
        var cmvkApiEndpoint: String = "https://api.agent-os.dev/cmvk",
        var cmvkApiKey: String = "",
        
        // Audit
        var auditRetentionDays: Int = 7,
        var auditLogToFile: Boolean = false,
        
        // Notifications
        var showBlockedNotifications: Boolean = true,
        var showWarningNotifications: Boolean = true
    )
    
    private var myState = State()
    
    override fun getState(): State = myState
    
    override fun loadState(state: State) {
        myState = state
    }
    
    companion object {
        fun getInstance(): AgentOSSettings {
            return ApplicationManager.getApplication().getService(AgentOSSettings::class.java)
        }
    }
}
