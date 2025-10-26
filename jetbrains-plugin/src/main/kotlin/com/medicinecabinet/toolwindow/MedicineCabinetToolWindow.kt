package com.medicinecabinet.toolwindow

import com.intellij.openapi.fileChooser.FileChooser
import com.intellij.openapi.fileChooser.FileChooserDescriptor
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.table.JBTable
import com.medicinecabinet.parser.BinaryParser
import java.awt.BorderLayout
import java.awt.Dimension
import javax.swing.*
import javax.swing.table.DefaultTableModel

class MedicineCabinetToolWindow(private val project: Project) {
    
    private val capsulesTableModel = DefaultTableModel(
        arrayOf("Name", "Project", "Created", "Sections"),
        0
    )
    private val tabletsTableModel = DefaultTableModel(
        arrayOf("Name", "Title", "Created", "Entries"),
        0
    )
    
    private val capsulesTable = JBTable(capsulesTableModel)
    private val tabletsTable = JBTable(tabletsTableModel)
    
    private val capsules = mutableListOf<Pair<String, BinaryParser.Capsule>>()
    private val tablets = mutableListOf<Pair<String, BinaryParser.Tablet>>()
    
    fun getContent(): JComponent {
        val panel = JPanel(BorderLayout())
        
        // Create tabs
        val tabbedPane = JTabbedPane()
        
        // Capsules tab
        val capsulesPanel = createCapsulesPanel()
        tabbedPane.addTab("Capsules (${capsules.size})", capsulesPanel)
        
        // Tablets tab
        val tabletsPanel = createTabletsPanel()
        tabbedPane.addTab("Tablets (${tablets.size})", tabletsPanel)
        
        panel.add(tabbedPane, BorderLayout.CENTER)
        
        // Toolbar
        val toolbar = createToolbar()
        panel.add(toolbar, BorderLayout.NORTH)
        
        panel.preferredSize = Dimension(400, 600)
        return panel
    }
    
    private fun createCapsulesPanel(): JComponent {
        val panel = JPanel(BorderLayout())
        
        capsulesTable.fillsViewportHeight = true
        val scrollPane = JBScrollPane(capsulesTable)
        panel.add(scrollPane, BorderLayout.CENTER)
        
        val buttonPanel = JPanel()
        val loadButton = JButton("Load Capsule")
        loadButton.addActionListener { loadCapsule() }
        
        val copyButton = JButton("Copy Context")
        copyButton.addActionListener { copySelectedCapsuleContext() }
        
        val removeButton = JButton("Remove")
        removeButton.addActionListener { removeSelectedCapsule() }
        
        buttonPanel.add(loadButton)
        buttonPanel.add(copyButton)
        buttonPanel.add(removeButton)
        
        panel.add(buttonPanel, BorderLayout.SOUTH)
        
        return panel
    }
    
    private fun createTabletsPanel(): JComponent {
        val panel = JPanel(BorderLayout())
        
        tabletsTable.fillsViewportHeight = true
        val scrollPane = JBScrollPane(tabletsTable)
        panel.add(scrollPane, BorderLayout.CENTER)
        
        val buttonPanel = JPanel()
        val loadButton = JButton("Load Tablet")
        loadButton.addActionListener { loadTablet() }
        
        val viewButton = JButton("View Details")
        viewButton.addActionListener { viewSelectedTablet() }
        
        val removeButton = JButton("Remove")
        removeButton.addActionListener { removeSelectedTablet() }
        
        buttonPanel.add(loadButton)
        buttonPanel.add(viewButton)
        buttonPanel.add(removeButton)
        
        panel.add(buttonPanel, BorderLayout.SOUTH)
        
        return panel
    }
    
    private fun createToolbar(): JComponent {
        val toolbar = JPanel()
        val label = JLabel("💊 Medicine Cabinet")
        label.font = label.font.deriveFont(16f)
        toolbar.add(label)
        return toolbar
    }
    
    private fun loadCapsule() {
        val descriptor = FileChooserDescriptor(true, false, false, false, false, false)
            .withFileFilter { it.extension == "auractx" }
            .withTitle("Select Capsule File")
            .withDescription("Choose a .auractx file to load")
        
        FileChooser.chooseFile(descriptor, project, null) { file ->
            try {
                val data = file.contentsToByteArray()
                val capsule = BinaryParser.parseCapsule(data)
                
                capsules.add(file.name to capsule)
                
                capsulesTableModel.addRow(arrayOf(
                    file.name,
                    capsule.metadata["raw"]?.toString()?.take(30) ?: "Unknown",
                    capsule.createdAt.toString(),
                    capsule.sections.size
                ))
                
                Messages.showInfoMessage(
                    project,
                    "Capsule loaded successfully: ${file.name}",
                    "Medicine Cabinet"
                )
            } catch (e: Exception) {
                Messages.showErrorDialog(
                    project,
                    "Failed to load capsule: ${e.message}",
                    "Error"
                )
            }
        }
    }
    
    private fun loadTablet() {
        val descriptor = FileChooserDescriptor(true, false, false, false, false, false)
            .withFileFilter { it.extension == "auratab" }
            .withTitle("Select Tablet File")
            .withDescription("Choose a .auratab file to load")
        
        FileChooser.chooseFile(descriptor, project, null) { file ->
            try {
                val data = file.contentsToByteArray()
                val tablet = BinaryParser.parseTablet(data)
                
                tablets.add(file.name to tablet)
                
                tabletsTableModel.addRow(arrayOf(
                    file.name,
                    tablet.metadata["raw"]?.toString()?.take(30) ?: "Unknown",
                    tablet.createdAt.toString(),
                    tablet.entries.size
                ))
                
                Messages.showInfoMessage(
                    project,
                    "Tablet loaded successfully: ${file.name}",
                    "Medicine Cabinet"
                )
            } catch (e: Exception) {
                Messages.showErrorDialog(
                    project,
                    "Failed to load tablet: ${e.message}",
                    "Error"
                )
            }
        }
    }
    
    private fun copySelectedCapsuleContext() {
        val selectedRow = capsulesTable.selectedRow
        if (selectedRow < 0) {
            Messages.showWarningDialog(project, "Please select a capsule first", "No Selection")
            return
        }
        
        val (filename, capsule) = capsules[selectedRow]
        val context = formatCapsuleContext(filename, capsule)
        
        val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
        clipboard.setContents(java.awt.datatransfer.StringSelection(context), null)
        
        Messages.showInfoMessage(project, "Context copied to clipboard!", "Success")
    }
    
    private fun formatCapsuleContext(filename: String, capsule: BinaryParser.Capsule): String {
        val sb = StringBuilder()
        sb.appendLine("## 💊 Medicine Cabinet Context")
        sb.appendLine()
        sb.appendLine("**File:** $filename")
        sb.appendLine("**Created:** ${capsule.createdAt}")
        sb.appendLine("**Version:** ${capsule.version}")
        sb.appendLine()
        
        capsule.sections.forEach { section ->
            sb.appendLine("### ${section.name}")
            when (section.kind) {
                BinaryParser.SectionKind.TEXT -> sb.appendLine(section.getTextPayload())
                BinaryParser.SectionKind.JSON -> sb.appendLine("```json\n${section.getJsonPayload()}\n```")
                BinaryParser.SectionKind.BINARY -> sb.appendLine("[Binary data: ${section.payload.size} bytes]")
            }
            sb.appendLine()
        }
        
        return sb.toString()
    }
    
    private fun viewSelectedTablet() {
        val selectedRow = tabletsTable.selectedRow
        if (selectedRow < 0) {
            Messages.showWarningDialog(project, "Please select a tablet first", "No Selection")
            return
        }
        
        val (filename, tablet) = tablets[selectedRow]
        val details = formatTabletDetails(filename, tablet)
        
        Messages.showInfoMessage(project, details, "Tablet Details")
    }
    
    private fun formatTabletDetails(filename: String, tablet: BinaryParser.Tablet): String {
        val sb = StringBuilder()
        sb.appendLine("File: $filename")
        sb.appendLine("Created: ${tablet.createdAt}")
        sb.appendLine("Entries: ${tablet.entries.size}")
        sb.appendLine()
        tablet.entries.take(5).forEach { entry ->
            sb.appendLine("• ${entry.path}")
        }
        if (tablet.entries.size > 5) {
            sb.appendLine("... and ${tablet.entries.size - 5} more")
        }
        return sb.toString()
    }
    
    private fun removeSelectedCapsule() {
        val selectedRow = capsulesTable.selectedRow
        if (selectedRow >= 0) {
            capsules.removeAt(selectedRow)
            capsulesTableModel.removeRow(selectedRow)
        }
    }
    
    private fun removeSelectedTablet() {
        val selectedRow = tabletsTable.selectedRow
        if (selectedRow >= 0) {
            tablets.removeAt(selectedRow)
            tabletsTableModel.removeRow(selectedRow)
        }
    }
}
