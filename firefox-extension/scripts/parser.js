/**
 * Medicine Cabinet Binary Parser
 * Parses .auractx (Context Capsule) and .auratab (Tablet) binary formats
 */

// Magic bytes and versions
const CAPSULE_MAGIC = new TextEncoder().encode('AURACTX1');
const TABLET_MAGIC = new TextEncoder().encode('AURATAB1');
const CAPSULE_VERSION = 1;
const TABLET_VERSION = 1;

// Section kinds for Capsules
const SectionKind = {
  TEXT: 1,
  JSON: 2,
  BINARY: 3
};

/**
 * DataView wrapper for big-endian reading
 */
class BinaryReader {
  constructor(arrayBuffer) {
    this.view = new DataView(arrayBuffer);
    this.cursor = 0;
  }

  readUint8() {
    const value = this.view.getUint8(this.cursor);
    this.cursor += 1;
    return value;
  }

  readUint16() {
    const value = this.view.getUint16(this.cursor, false); // big-endian
    this.cursor += 2;
    return value;
  }

  readUint32() {
    const value = this.view.getUint32(this.cursor, false); // big-endian
    this.cursor += 4;
    return value;
  }

  readUint64() {
    const value = this.view.getBigUint64(this.cursor, false); // big-endian
    this.cursor += 8;
    return value;
  }

  readBytes(length) {
    const bytes = new Uint8Array(this.view.buffer, this.cursor, length);
    this.cursor += length;
    return bytes;
  }

  readString() {
    const length = this.readUint32();
    const bytes = this.readBytes(length);
    return new TextDecoder('utf-8').decode(bytes);
  }

  hasMore() {
    return this.cursor < this.view.byteLength;
  }

  getRemainingBytes() {
    return this.view.byteLength - this.cursor;
  }
}

/**
 * Parse a Context Capsule (.auractx) file
 */
export function parseCapsule(arrayBuffer) {
  const reader = new BinaryReader(arrayBuffer);

  // Read magic
  const magic = reader.readBytes(8);
  if (!arraysEqual(magic, CAPSULE_MAGIC)) {
    throw new Error('Invalid capsule magic bytes');
  }

  // Read version
  const version = reader.readUint16();
  if (version !== CAPSULE_VERSION) {
    throw new Error(`Unsupported capsule version: ${version}`);
  }

  // Read created_at (epoch milliseconds)
  const createdAtMs = Number(reader.readUint64());
  const createdAt = new Date(createdAtMs);

  // Read metadata JSON
  const metadataJson = reader.readString();
  const metadata = JSON.parse(metadataJson);

  // Read section count
  const sectionCount = reader.readUint32();
  const sections = [];

  // Read each section
  for (let i = 0; i < sectionCount; i++) {
    const name = reader.readString();
    const kind = reader.readUint8();
    const payloadLength = reader.readUint32();
    const payload = reader.readBytes(payloadLength);

    let decodedPayload;
    if (kind === SectionKind.TEXT) {
      decodedPayload = new TextDecoder('utf-8').decode(payload);
    } else if (kind === SectionKind.JSON) {
      const jsonStr = new TextDecoder('utf-8').decode(payload);
      decodedPayload = JSON.parse(jsonStr);
    } else if (kind === SectionKind.BINARY) {
      decodedPayload = payload;
    } else {
      decodedPayload = payload;
    }

    sections.push({
      name,
      kind,
      kindName: Object.keys(SectionKind).find(k => SectionKind[k] === kind) || 'UNKNOWN',
      payload: decodedPayload,
      rawPayload: payload
    });
  }

  return {
    type: 'capsule',
    version,
    createdAt,
    metadata,
    sections
  };
}

/**
 * Parse a Tablet (.auratab) file
 */
export function parseTablet(arrayBuffer) {
  const reader = new BinaryReader(arrayBuffer);

  // Read magic
  const magic = reader.readBytes(8);
  if (!arraysEqual(magic, TABLET_MAGIC)) {
    throw new Error('Invalid tablet magic bytes');
  }

  // Read version
  const version = reader.readUint16();
  if (version !== TABLET_VERSION) {
    throw new Error(`Unsupported tablet version: ${version}`);
  }

  // Read created_at (epoch milliseconds)
  const createdAtMs = Number(reader.readUint64());
  const createdAt = new Date(createdAtMs);

  // Read metadata JSON
  const metadataJson = reader.readString();
  const metadata = JSON.parse(metadataJson);

  // Read entry count
  const entryCount = reader.readUint32();
  const entries = [];

  // Read each entry
  for (let i = 0; i < entryCount; i++) {
    const path = reader.readString();
    const diff = reader.readString();
    const notes = reader.readString();

    entries.push({
      path,
      diff,
      notes
    });
  }

  return {
    type: 'tablet',
    version,
    createdAt,
    metadata,
    entries
  };
}

/**
 * Auto-detect and parse either a Capsule or Tablet
 */
export function parse(arrayBuffer) {
  const magicBytes = new Uint8Array(arrayBuffer.slice(0, 8));
  
  if (arraysEqual(magicBytes, CAPSULE_MAGIC)) {
    return parseCapsule(arrayBuffer);
  } else if (arraysEqual(magicBytes, TABLET_MAGIC)) {
    return parseTablet(arrayBuffer);
  } else {
    throw new Error('Unknown file format (invalid magic bytes)');
  }
}

/**
 * Helper to compare Uint8Arrays
 */
function arraysEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

// For non-module usage
if (typeof window !== 'undefined') {
  window.MedicineCabinetParser = {
    parse,
    parseCapsule,
    parseTablet,
    SectionKind
  };
}
