package com.agentos.plugin.toolwindow

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBList
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.content.ContentFactory
import com.agentos.plugin.settings.AgentOSSettings
import java.awt.BorderLayout
import javax.swing.DefaultListModel
import javax.swing.JPanel

/**
 * Factory for the Agent OS tool window.
 */
class AgentOSToolWindowFactory : ToolWindowFactory {
    
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val panel = AgentOSToolWindowPanel(project)
        val content = ContentFactory.getInstance().createContent(panel, "", false)
        toolWindow.contentManager.addContent(content)
    }
}

/**
 * Main panel for the Agent OS tool window.
 */
class AgentOSToolWindowPanel(private val project: Project) : JPanel(BorderLayout()) {
    
    init {
        val settings = AgentOSSettings.getInstance().state
        
        // Status header
        val statusLabel = JBLabel(
            if (settings.enabled) "🛡️ Agent OS: Active" else "⚠️ Agent OS: Disabled"
        )
        add(statusLabel, BorderLayout.NORTH)
        
        // Audit log list
        val listModel = DefaultListModel<String>()
        listModel.addElement("✅ Project opened - ${java.time.LocalDateTime.now()}")
        listModel.addElement("🔍 Scanning enabled files...")
        
        if (settings.blockDestructiveSQL) {
            listModel.addElement("📋 Policy: Destructive SQL blocking enabled")
        }
        if (settings.blockSecretExposure) {
            listModel.addElement("📋 Policy: Secret exposure blocking enabled")
        }
        if (settings.blockFileDeletes) {
            listModel.addElement("📋 Policy: Dangerous file ops blocking enabled")
        }
        
        val auditList = JBList(listModel)
        add(JBScrollPane(auditList), BorderLayout.CENTER)
        
        // Footer with stats
        val statsLabel = JBLabel("Blocked: 0 | Warnings: 0 | Reviews: 0")
        add(statsLabel, BorderLayout.SOUTH)
    }
}
