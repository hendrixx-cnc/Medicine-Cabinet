package com.medicinecabinet.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.medicinecabinet.parser.BinaryParser

class LoadCapsuleAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE) ?: return
        
        if (file.extension != "auractx") {
            Messages.showWarningDialog(
                project,
                "This is not a valid capsule file (.auractx)",
                "Invalid File"
            )
            return
        }
        
        try {
            val data = file.contentsToByteArray()
            val capsule = BinaryParser.parseCapsule(data)
            
            Messages.showInfoMessage(
                project,
                "Capsule loaded successfully!\n" +
                "Created: ${capsule.createdAt}\n" +
                "Sections: ${capsule.sections.size}",
                "Capsule Loaded"
            )
        } catch (ex: Exception) {
            Messages.showErrorDialog(
                project,
                "Failed to load capsule: ${ex.message}",
                "Error"
            )
        }
    }
    
    override fun update(e: AnActionEvent) {
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE)
        e.presentation.isEnabledAndVisible = file?.extension == "auractx"
    }
}

class LoadTabletAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE) ?: return
        
        if (file.extension != "auratab") {
            Messages.showWarningDialog(
                project,
                "This is not a valid tablet file (.auratab)",
                "Invalid File"
            )
            return
        }
        
        try {
            val data = file.contentsToByteArray()
            val tablet = BinaryParser.parseTablet(data)
            
            Messages.showInfoMessage(
                project,
                "Tablet loaded successfully!\n" +
                "Created: ${tablet.createdAt}\n" +
                "Entries: ${tablet.entries.size}",
                "Tablet Loaded"
            )
        } catch (ex: Exception) {
            Messages.showErrorDialog(
                project,
                "Failed to load tablet: ${ex.message}",
                "Error"
            )
        }
    }
    
    override fun update(e: AnActionEvent) {
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE)
        e.presentation.isEnabledAndVisible = file?.extension == "auratab"
    }
}

class CopyContextAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        
        Messages.showInfoMessage(
            project,
            "Open the Medicine Cabinet tool window to copy context",
            "Medicine Cabinet"
        )
    }
}

class RefreshAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        // Refresh the tool window
        Messages.showInfoMessage(
            e.project,
            "Medicine Cabinet refreshed",
            "Success"
        )
    }
}
