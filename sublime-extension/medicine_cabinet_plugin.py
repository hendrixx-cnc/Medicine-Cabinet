"""
Medicine Cabinet Plugin for Sublime Text
Provides AI memory management with .auractx and .auratab support
"""

import sublime
import sublime_plugin
import struct
import os
from typing import Dict, List, Tuple, Optional


class BinaryParser:
    """Parser for AURACTX1 and AURATAB1 binary formats"""
    
    @staticmethod
    def parse_capsule(data: bytes) -> Dict:
        """Parse AURACTX1 format"""
        if len(data) < 16:
            raise ValueError("Invalid capsule: too short")
        
        # Read header
        magic = data[0:8].decode('ascii')
        if magic != 'AURACTX1':
            raise ValueError(f"Invalid magic: {magic}")
        
        version = struct.unpack('>I', data[8:12])[0]
        section_count = struct.unpack('>I', data[12:16])[0]
        
        sections = []
        offset = 16
        
        for _ in range(section_count):
            if offset + 12 > len(data):
                break
            
            section_type = struct.unpack('>I', data[offset:offset+4])[0]
            section_length = struct.unpack('>Q', data[offset+4:offset+12])[0]
            offset += 12
            
            if offset + section_length > len(data):
                break
            
            section_data = data[offset:offset+section_length]
            offset += section_length
            
            type_map = {1: 'TEXT', 2: 'JSON', 3: 'BINARY'}
            sections.append({
                'type': type_map.get(section_type, 'UNKNOWN'),
                'data': section_data.decode('utf-8', errors='replace') if section_type in [1, 2] else section_data
            })
        
        return {
            'type': 'capsule',
            'version': version,
            'sections': sections
        }
    
    @staticmethod
    def parse_tablet(data: bytes) -> Dict:
        """Parse AURATAB1 format"""
        if len(data) < 16:
            raise ValueError("Invalid tablet: too short")
        
        # Read header
        magic = data[0:8].decode('ascii')
        if magic != 'AURATAB1':
            raise ValueError(f"Invalid magic: {magic}")
        
        version = struct.unpack('>I', data[8:12])[0]
        entry_count = struct.unpack('>I', data[12:16])[0]
        
        entries = []
        offset = 16
        
        for _ in range(entry_count):
            if offset + 20 > len(data):
                break
            
            path_length = struct.unpack('>I', data[offset:offset+4])[0]
            diff_length = struct.unpack('>Q', data[offset+4:offset+12])[0]
            notes_length = struct.unpack('>Q', data[offset+12:offset+20])[0]
            offset += 20
            
            if offset + path_length + diff_length + notes_length > len(data):
                break
            
            path = data[offset:offset+path_length].decode('utf-8', errors='replace')
            offset += path_length
            
            diff = data[offset:offset+diff_length].decode('utf-8', errors='replace')
            offset += diff_length
            
            notes = data[offset:offset+notes_length].decode('utf-8', errors='replace')
            offset += notes_length
            
            entries.append({
                'path': path,
                'diff': diff,
                'notes': notes
            })
        
        return {
            'type': 'tablet',
            'version': version,
            'entries': entries
        }


class MedicineCabinetState:
    """Global state for loaded capsules and tablets"""
    capsules: List[Dict] = []
    tablets: List[Dict] = []
    current_file: Optional[str] = None


class LoadCapsuleCommand(sublime_plugin.WindowCommand):
    """Load a Context Capsule file"""
    
    def run(self):
        self.window.show_open_dialog(
            self.on_done,
            file_types=[("Context Capsule", ["auractx"])],
            multi_select=False
        )
    
    def on_done(self, path):
        if not path:
            return
        
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            capsule = BinaryParser.parse_capsule(data)
            capsule['filename'] = os.path.basename(path)
            capsule['path'] = path
            
            MedicineCabinetState.capsules.append(capsule)
            MedicineCabinetState.current_file = path
            
            sublime.status_message(f"Loaded capsule: {capsule['filename']}")
            self.window.run_command('show_medicine_cabinet_panel')
            
        except Exception as e:
            sublime.error_message(f"Failed to load capsule: {str(e)}")


class LoadTabletCommand(sublime_plugin.WindowCommand):
    """Load a Memory Tablet file"""
    
    def run(self):
        self.window.show_open_dialog(
            self.on_done,
            file_types=[("Memory Tablet", ["auratab"])],
            multi_select=False
        )
    
    def on_done(self, path):
        if not path:
            return
        
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            tablet = BinaryParser.parse_tablet(data)
            tablet['filename'] = os.path.basename(path)
            tablet['path'] = path
            
            MedicineCabinetState.tablets.append(tablet)
            MedicineCabinetState.current_file = path
            
            sublime.status_message(f"Loaded tablet: {tablet['filename']}")
            self.window.run_command('show_medicine_cabinet_panel')
            
        except Exception as e:
            sublime.error_message(f"Failed to load tablet: {str(e)}")


class LoadCapsuleFromContextCommand(sublime_plugin.TextCommand):
    """Load capsule from context menu"""
    
    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path or not file_path.endswith('.auractx'):
            sublime.error_message("Not a .auractx file")
            return
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            capsule = BinaryParser.parse_capsule(data)
            capsule['filename'] = os.path.basename(file_path)
            capsule['path'] = file_path
            
            MedicineCabinetState.capsules.append(capsule)
            MedicineCabinetState.current_file = file_path
            
            sublime.status_message(f"Loaded capsule: {capsule['filename']}")
            self.view.window().run_command('show_medicine_cabinet_panel')
            
        except Exception as e:
            sublime.error_message(f"Failed to load capsule: {str(e)}")
    
    def is_visible(self):
        file_path = self.view.file_name()
        return file_path and file_path.endswith('.auractx')


class LoadTabletFromContextCommand(sublime_plugin.TextCommand):
    """Load tablet from context menu"""
    
    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path or not file_path.endswith('.auratab'):
            sublime.error_message("Not a .auratab file")
            return
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            tablet = BinaryParser.parse_tablet(data)
            tablet['filename'] = os.path.basename(file_path)
            tablet['path'] = file_path
            
            MedicineCabinetState.tablets.append(tablet)
            MedicineCabinetState.current_file = file_path
            
            sublime.status_message(f"Loaded tablet: {tablet['filename']}")
            self.view.window().run_command('show_medicine_cabinet_panel')
            
        except Exception as e:
            sublime.error_message(f"Failed to load tablet: {str(e)}")
    
    def is_visible(self):
        file_path = self.view.file_name()
        return file_path and file_path.endswith('.auratab')


class ShowMedicineCabinetPanelCommand(sublime_plugin.WindowCommand):
    """Show the Medicine Cabinet output panel"""
    
    def run(self):
        output_view = self.window.create_output_panel("medicine_cabinet")
        output_view.settings().set("word_wrap", True)
        output_view.settings().set("line_numbers", False)
        
        content = self.generate_content()
        output_view.run_command('append', {'characters': content})
        
        self.window.run_command("show_panel", {"panel": "output.medicine_cabinet"})
    
    def generate_content(self) -> str:
        """Generate panel content"""
        lines = []
        lines.append("=" * 80)
        lines.append("Medicine Cabinet - AI Memory Management")
        lines.append("=" * 80)
        lines.append("")
        
        # Capsules
        if MedicineCabinetState.capsules:
            lines.append(f"Context Capsules ({len(MedicineCabinetState.capsules)}):")
            lines.append("-" * 80)
            for i, capsule in enumerate(MedicineCabinetState.capsules):
                lines.append(f"\n[{i+1}] {capsule['filename']}")
                lines.append(f"    Version: {capsule['version']}")
                lines.append(f"    Sections: {len(capsule['sections'])}")
                
                for j, section in enumerate(capsule['sections']):
                    lines.append(f"    [{j+1}] {section['type']}")
                    if isinstance(section['data'], str):
                        preview = section['data'][:200].replace('\n', ' ')
                        if len(section['data']) > 200:
                            preview += "..."
                        lines.append(f"        {preview}")
            lines.append("")
        else:
            lines.append("No context capsules loaded.")
            lines.append("")
        
        # Tablets
        if MedicineCabinetState.tablets:
            lines.append(f"Memory Tablets ({len(MedicineCabinetState.tablets)}):")
            lines.append("-" * 80)
            for i, tablet in enumerate(MedicineCabinetState.tablets):
                lines.append(f"\n[{i+1}] {tablet['filename']}")
                lines.append(f"    Version: {tablet['version']}")
                lines.append(f"    Entries: {len(tablet['entries'])}")
                
                for j, entry in enumerate(tablet['entries']):
                    lines.append(f"    [{j+1}] {entry['path']}")
                    if entry['notes']:
                        notes_preview = entry['notes'][:100].replace('\n', ' ')
                        if len(entry['notes']) > 100:
                            notes_preview += "..."
                        lines.append(f"        Notes: {notes_preview}")
            lines.append("")
        else:
            lines.append("No memory tablets loaded.")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("Use Tools > Medicine Cabinet to load files")
        lines.append("=" * 80)
        
        return "\n".join(lines)


class CopyMedicineCabinetContextCommand(sublime_plugin.WindowCommand):
    """Copy all loaded context to clipboard"""
    
    def run(self):
        context_parts = []
        
        # Add capsules
        for capsule in MedicineCabinetState.capsules:
            context_parts.append(f"=== Context Capsule: {capsule['filename']} ===\n")
            for section in capsule['sections']:
                context_parts.append(f"[{section['type']}]\n")
                if isinstance(section['data'], str):
                    context_parts.append(section['data'])
                context_parts.append("\n\n")
        
        # Add tablets
        for tablet in MedicineCabinetState.tablets:
            context_parts.append(f"=== Memory Tablet: {tablet['filename']} ===\n")
            for entry in tablet['entries']:
                context_parts.append(f"File: {entry['path']}\n")
                if entry['notes']:
                    context_parts.append(f"Notes: {entry['notes']}\n")
                if entry['diff']:
                    context_parts.append(f"Changes:\n{entry['diff']}\n")
                context_parts.append("\n")
        
        if context_parts:
            context = "".join(context_parts)
            sublime.set_clipboard(context)
            sublime.status_message(f"Copied context ({len(context)} chars)")
        else:
            sublime.status_message("No context loaded")
    
    def is_enabled(self):
        return bool(MedicineCabinetState.capsules or MedicineCabinetState.tablets)
