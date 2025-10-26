package com.medicinecabinet.parser

import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.charset.StandardCharsets
import java.time.Instant

/**
 * Binary parser for Medicine Cabinet file formats
 */
object BinaryParser {
    
    private val CAPSULE_MAGIC = "AURACTX1".toByteArray(StandardCharsets.US_ASCII)
    private val TABLET_MAGIC = "AURATAB1".toByteArray(StandardCharsets.US_ASCII)
    
    enum class SectionKind(val value: Int) {
        TEXT(1),
        JSON(2),
        BINARY(3)
    }
    
    data class CapsuleSection(
        val name: String,
        val kind: SectionKind,
        val payload: ByteArray
    ) {
        fun getTextPayload(): String = String(payload, StandardCharsets.UTF_8)
        fun getJsonPayload(): String = String(payload, StandardCharsets.UTF_8)
    }
    
    data class Capsule(
        val version: Int,
        val createdAt: Instant,
        val metadata: Map<String, Any>,
        val sections: List<CapsuleSection>
    )
    
    data class TabletEntry(
        val path: String,
        val diff: String,
        val notes: String
    )
    
    data class Tablet(
        val version: Int,
        val createdAt: Instant,
        val metadata: Map<String, Any>,
        val entries: List<TabletEntry>
    )
    
    fun parseCapsule(data: ByteArray): Capsule {
        val buffer = ByteBuffer.wrap(data).order(ByteOrder.BIG_ENDIAN)
        
        // Read and verify magic
        val magic = ByteArray(8)
        buffer.get(magic)
        require(magic.contentEquals(CAPSULE_MAGIC)) { "Invalid capsule magic bytes" }
        
        // Read version
        val version = buffer.short.toInt()
        require(version == 1) { "Unsupported capsule version: $version" }
        
        // Read created_at (epoch milliseconds)
        val createdAtMs = buffer.long
        val createdAt = Instant.ofEpochMilli(createdAtMs)
        
        // Read metadata JSON
        val metadataJson = readString(buffer)
        val metadata = parseJsonToMap(metadataJson)
        
        // Read section count
        val sectionCount = buffer.int
        val sections = mutableListOf<CapsuleSection>()
        
        // Read each section
        repeat(sectionCount) {
            val name = readString(buffer)
            val kindValue = buffer.get().toInt()
            val kind = SectionKind.values().find { it.value == kindValue } 
                ?: SectionKind.BINARY
            val payloadLength = buffer.int
            val payload = ByteArray(payloadLength)
            buffer.get(payload)
            
            sections.add(CapsuleSection(name, kind, payload))
        }
        
        return Capsule(version, createdAt, metadata, sections)
    }
    
    fun parseTablet(data: ByteArray): Tablet {
        val buffer = ByteBuffer.wrap(data).order(ByteOrder.BIG_ENDIAN)
        
        // Read and verify magic
        val magic = ByteArray(8)
        buffer.get(magic)
        require(magic.contentEquals(TABLET_MAGIC)) { "Invalid tablet magic bytes" }
        
        // Read version
        val version = buffer.short.toInt()
        require(version == 1) { "Unsupported tablet version: $version" }
        
        // Read created_at (epoch milliseconds)
        val createdAtMs = buffer.long
        val createdAt = Instant.ofEpochMilli(createdAtMs)
        
        // Read metadata JSON
        val metadataJson = readString(buffer)
        val metadata = parseJsonToMap(metadataJson)
        
        // Read entry count
        val entryCount = buffer.int
        val entries = mutableListOf<TabletEntry>()
        
        // Read each entry
        repeat(entryCount) {
            val path = readString(buffer)
            val diff = readString(buffer)
            val notes = readString(buffer)
            entries.add(TabletEntry(path, diff, notes))
        }
        
        return Tablet(version, createdAt, metadata, entries)
    }
    
    private fun readString(buffer: ByteBuffer): String {
        val length = buffer.int
        val bytes = ByteArray(length)
        buffer.get(bytes)
        return String(bytes, StandardCharsets.UTF_8)
    }
    
    private fun parseJsonToMap(json: String): Map<String, Any> {
        // Simple JSON parsing - in production, use a proper JSON library
        // For now, return a placeholder map
        return mapOf("raw" to json)
    }
}
