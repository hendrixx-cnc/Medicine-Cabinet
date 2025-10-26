package com.medicinecabinet.filetype

import com.intellij.openapi.fileTypes.FileType
import com.intellij.openapi.vfs.VirtualFile
import javax.swing.Icon

class CapsuleFileType : FileType {
    
    companion object {
        val INSTANCE = CapsuleFileType()
    }
    
    override fun getName() = "AURACTX File"
    
    override fun getDescription() = "Medicine Cabinet Context Capsule"
    
    override fun getDefaultExtension() = "auractx"
    
    override fun getIcon(): Icon? = null // Add custom icon here
    
    override fun isBinary() = true
    
    override fun isReadOnly() = false
}

class TabletFileType : FileType {
    
    companion object {
        val INSTANCE = TabletFileType()
    }
    
    override fun getName() = "AURATAB File"
    
    override fun getDescription() = "Medicine Cabinet Memory Tablet"
    
    override fun getDefaultExtension() = "auratab"
    
    override fun getIcon(): Icon? = null // Add custom icon here
    
    override fun isBinary() = true
    
    override fun isReadOnly() = false
}
