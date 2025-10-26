package com.medicinecabinet.icons

import com.intellij.ide.IconProvider
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiFile
import javax.swing.Icon

class MedicineCabinetIconProvider : IconProvider() {
    
    override fun getIcon(element: PsiElement, flags: Int): Icon? {
        if (element is PsiFile) {
            val extension = element.virtualFile?.extension
            when (extension) {
                "auractx" -> return null // Add custom capsule icon
                "auratab" -> return null // Add custom tablet icon
            }
        }
        return null
    }
}
