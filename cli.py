#!/usr/bin/env python3
"""
Medicine Cabinet CLI - Command-line interface for managing AI memory.

Usage:
    medicine-cabinet capsule create <project> <summary> [options]
    medicine-cabinet capsule read <file>
    medicine-cabinet capsule set-task <file> <objective>
    medicine-cabinet capsule set-files <file> <file1> [<file2> ...]
    medicine-cabinet tablet create <title> <description> [options]
    medicine-cabinet tablet read <file>
    medicine-cabinet tablet add-entry <file> <path> [options]
    medicine-cabinet sessions [--dir <path>]
    medicine-cabinet view <file>
    medicine-cabinet inspect <file>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from context_capsule import (
    ContextCapsule,
    CapsuleMetadata,
    CapsuleSection,
    load_capsule,
)
from tablet import Tablet, TabletMetadata, TabletEntry, load_tablet


def cmd_capsule_create(args):
    """Create a new context capsule."""
    metadata = CapsuleMetadata(
        project=args.project,
        summary=args.summary,
        author=args.author,
        branch=args.branch,
    )
    capsule = ContextCapsule(metadata=metadata)
    
    output_path = Path(args.output or f"{args.project.lower().replace(' ', '_')}.auractx")
    capsule.write(output_path)
    print(f"✓ Created capsule: {output_path}")


def cmd_capsule_read(args):
    """Read and display a context capsule."""
    capsule = load_capsule(args.file)
    
    print("=" * 80)
    print(f"Context Capsule: {args.file}")
    print("=" * 80)
    print(f"Project: {capsule.metadata.project}")
    print(f"Summary: {capsule.metadata.summary}")
    print(f"Author: {capsule.metadata.author or 'N/A'}")
    print(f"Created: {capsule.metadata.created_at.isoformat()}")
    print(f"Branch: {capsule.metadata.branch or 'N/A'}")
    print("-" * 80)
    
    if capsule.get_task_objective():
        print(f"\nTask Objective:\n  {capsule.get_task_objective()}")
    
    if capsule.get_relevant_files():
        print(f"\nRelevant Files:")
        for f in capsule.get_relevant_files():
            print(f"  - {f}")
    
    if capsule.get_working_plan():
        print(f"\nWorking Plan:")
        plan = capsule.get_working_plan()
        if isinstance(plan, list):
            for i, step in enumerate(plan, 1):
                print(f"  {i}. {step}")
        else:
            print(f"  {plan}")
    
    if capsule.get_error_state():
        print(f"\nLast Error:\n  {capsule.get_error_state()}")
    
    print("\n" + "=" * 80)


def cmd_capsule_set_task(args):
    """Set the task objective in a capsule."""
    capsule = load_capsule(args.file)
    capsule.set_task_objective(args.objective)
    capsule.write(args.file)
    print(f"✓ Updated task objective in {args.file}")


def cmd_capsule_set_files(args):
    """Set the relevant files in a capsule."""
    capsule = load_capsule(args.file)
    capsule.set_relevant_files(args.files)
    capsule.write(args.file)
    print(f"✓ Updated relevant files in {args.file} ({len(args.files)} files)")


def cmd_tablet_create(args):
    """Create a new tablet."""
    metadata = TabletMetadata(
        title=args.title,
        summary=args.description,
        author=args.author,
        tags=args.tags or [],
    )
    tablet = Tablet(metadata=metadata, version=1)
    
    output_path = Path(args.output or f"{args.title.lower().replace(' ', '_')}.auratab")
    tablet.write(output_path)
    print(f"✓ Created tablet: {output_path}")


def cmd_tablet_read(args):
    """Read and display a tablet."""
    tablet = load_tablet(args.file)
    
    print("=" * 80)
    print(f"Tablet: {args.file}")
    print("=" * 80)
    print(f"Title: {tablet.metadata.title}")
    print(f"Description: {tablet.metadata.description}")
    print(f"Author: {tablet.metadata.author or 'N/A'}")
    print(f"Created: {tablet.created_at.isoformat()}")
    print(f"Tags: {', '.join(tablet.metadata.tags) if tablet.metadata.tags else 'None'}")
    print(f"Entries: {len(tablet.entries)}")
    print("-" * 80)
    
    for i, entry in enumerate(tablet.entries, 1):
        print(f"\n[Entry {i}]")
        print(f"  Path: {entry.path}")
        if entry.notes:
            print(f"  Notes: {entry.notes[:100]}{'...' if len(entry.notes) > 100 else ''}")
        if entry.diff:
            print(f"  Diff: {len(entry.diff)} characters")
    
    print("\n" + "=" * 80)


def cmd_tablet_add_entry(args):
    """Add an entry to an existing tablet."""
    tablet = load_tablet(args.file)
    
    diff = ""
    if args.diff_file:
        diff = Path(args.diff_file).read_text()
    elif args.diff:
        diff = args.diff
    
    entry = TabletEntry(
        path=args.path,
        diff=diff,
        notes=args.notes or "",
    )
    
    tablet.add_entry(entry)
    tablet.write(args.file)
    print(f"✓ Added entry to {args.file}: {args.path}")


def cmd_inspect(args):
    """Inspect any Medicine Cabinet file."""
    from inspector import main as inspector_main
    sys.argv = ["inspector", str(args.file)]
    inspector_main()


def cmd_sessions_list(args):
    """List all session files in a directory."""
    sessions_dir = Path(args.dir)
    
    if not sessions_dir.exists():
        print(f"Directory not found: {sessions_dir}")
        sys.exit(1)
    
    # Find all session files
    tablets = list(sessions_dir.glob("*.auratab"))
    capsules = list(sessions_dir.glob("*.auractx"))
    
    if not tablets and not capsules:
        print(f"No session files found in {sessions_dir}")
        return
    
    print("=" * 80)
    print(f"Sessions in {sessions_dir}")
    print("=" * 80)
    
    # List tablets
    if tablets:
        print(f"\nTablets ({len(tablets)}):")
        print("-" * 80)
        for tablet_path in sorted(tablets):
            try:
                tablet = load_tablet(str(tablet_path))
                print(f"\n  📄 {tablet_path.name}")
                print(f"     Title: {tablet.metadata.title}")
                print(f"     Entries: {len(tablet.entries)}")
                print(f"     Created: {tablet.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"\n  ⚠️  {tablet_path.name} (error: {e})")
    
    # List capsules
    if capsules:
        print(f"\nCapsules ({len(capsules)}):")
        print("-" * 80)
        for capsule_path in sorted(capsules):
            try:
                capsule = load_capsule(str(capsule_path))
                print(f"\n  📦 {capsule_path.name}")
                print(f"     Project: {capsule.metadata.project}")
                print(f"     Sections: {len(capsule.sections)}")
                print(f"     Created: {capsule.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"\n  ⚠️  {capsule_path.name} (error: {e})")
    
    print("\n" + "=" * 80)


def cmd_view_file(args):
    """View detailed contents of a session file."""
    filepath = Path(args.file)
    
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)
    
    if filepath.suffix == ".auratab":
        _view_tablet_detailed(filepath)
    elif filepath.suffix == ".auractx":
        _view_capsule_detailed(filepath)
    else:
        print(f"Unknown file type: {filepath.suffix}")
        print("Expected .auratab or .auractx file")
        sys.exit(1)


def _view_tablet_detailed(filepath: Path):
    """Pretty-print tablet file contents."""
    tablet = load_tablet(str(filepath))
    
    print("=" * 80)
    print(f"TABLET: {filepath.name}")
    print("=" * 80)
    print(f"\nTitle:       {tablet.metadata.title}")
    print(f"Description: {tablet.metadata.description}")
    print(f"Author:      {tablet.metadata.author or 'N/A'}")
    print(f"Created:     {tablet.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    if tablet.metadata.tags:
        print(f"Tags:        {', '.join(tablet.metadata.tags)}")
    
    print(f"\nTotal Entries: {len(tablet.entries)}")
    print("-" * 80)
    
    for i, entry in enumerate(tablet.entries, 1):
        print(f"\n[Entry {i}] {entry.path}")
        
        if entry.notes:
            print(f"\n  Notes:")
            notes_lines = entry.notes.split('\n')
            for line in notes_lines[:10]:
                print(f"    {line}")
            if len(notes_lines) > 10:
                print(f"    ... ({len(notes_lines) - 10} more lines)")
        
        if entry.diff:
            print(f"\n  Diff ({len(entry.diff)} characters):")
            diff_lines = entry.diff.split('\n')
            for line in diff_lines[:15]:
                print(f"    {line}")
            if len(diff_lines) > 15:
                print(f"    ... ({len(diff_lines) - 15} more lines)")
    
    print("\n" + "=" * 80)


def _view_capsule_detailed(filepath: Path):
    """Pretty-print capsule file contents."""
    capsule = load_capsule(str(filepath))
    
    print("=" * 80)
    print(f"CAPSULE: {filepath.name}")
    print("=" * 80)
    print(f"\nProject:     {capsule.metadata.project}")
    print(f"Summary:     {capsule.metadata.summary}")
    print(f"Author:      {capsule.metadata.author or 'N/A'}")
    print(f"Created:     {capsule.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Branch:      {capsule.metadata.branch or 'N/A'}")
    
    if capsule.get_task_objective():
        print(f"\nTask:        {capsule.get_task_objective()}")
    
    if capsule.get_relevant_files():
        print(f"\nRelevant Files ({len(capsule.get_relevant_files())}):")
        for f in capsule.get_relevant_files()[:5]:
            print(f"  - {f}")
        if len(capsule.get_relevant_files()) > 5:
            print(f"  ... and {len(capsule.get_relevant_files()) - 5} more")
    
    print(f"\nTotal Sections: {len(capsule.sections)}")
    print("-" * 80)
    
    for i, section in enumerate(capsule.sections, 1):
        print(f"\n[Section {i}] {section.name} ({section.kind.name})")
        
        if section.kind.name == "BINARY":
            print(f"  Binary data: {len(section.payload)} bytes")
        else:
            # TEXT or JSON
            try:
                content = section.payload.decode('utf-8')
                lines = content.split('\n')
                print(f"  Content ({len(content)} characters):")
                for line in lines[:10]:
                    print(f"    {line}")
                if len(lines) > 10:
                    print(f"    ... ({len(lines) - 10} more lines)")
            except:
                print(f"  Data: {len(section.payload)} bytes")
    
    print("\n" + "=" * 80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Medicine Cabinet - AI Agent Memory Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Capsule commands
    capsule_parser = subparsers.add_parser("capsule", help="Manage context capsules")
    capsule_subparsers = capsule_parser.add_subparsers(dest="capsule_command")
    
    # capsule create
    capsule_create = capsule_subparsers.add_parser("create", help="Create a new capsule")
    capsule_create.add_argument("project", help="Project name")
    capsule_create.add_argument("summary", help="Brief summary")
    capsule_create.add_argument("--author", help="Author name")
    capsule_create.add_argument("--branch", help="Git branch")
    capsule_create.add_argument("-o", "--output", help="Output file path")
    capsule_create.set_defaults(func=cmd_capsule_create)
    
    # capsule read
    capsule_read = capsule_subparsers.add_parser("read", help="Read a capsule")
    capsule_read.add_argument("file", help="Capsule file path")
    capsule_read.set_defaults(func=cmd_capsule_read)
    
    # capsule set-task
    capsule_task = capsule_subparsers.add_parser("set-task", help="Set task objective")
    capsule_task.add_argument("file", help="Capsule file path")
    capsule_task.add_argument("objective", help="Task objective")
    capsule_task.set_defaults(func=cmd_capsule_set_task)
    
    # capsule set-files
    capsule_files = capsule_subparsers.add_parser("set-files", help="Set relevant files")
    capsule_files.add_argument("file", help="Capsule file path")
    capsule_files.add_argument("files", nargs="+", help="File paths")
    capsule_files.set_defaults(func=cmd_capsule_set_files)
    
    # Tablet commands
    tablet_parser = subparsers.add_parser("tablet", help="Manage tablets")
    tablet_subparsers = tablet_parser.add_subparsers(dest="tablet_command")
    
    # tablet create
    tablet_create = tablet_subparsers.add_parser("create", help="Create a new tablet")
    tablet_create.add_argument("title", help="Tablet title")
    tablet_create.add_argument("description", help="Tablet description")
    tablet_create.add_argument("--author", help="Author name")
    tablet_create.add_argument("--tags", nargs="+", help="Tags")
    tablet_create.add_argument("-o", "--output", help="Output file path")
    tablet_create.set_defaults(func=cmd_tablet_create)
    
    # tablet read
    tablet_read = tablet_subparsers.add_parser("read", help="Read a tablet")
    tablet_read.add_argument("file", help="Tablet file path")
    tablet_read.set_defaults(func=cmd_tablet_read)
    
    # tablet add-entry
    tablet_entry = tablet_subparsers.add_parser("add-entry", help="Add entry to tablet")
    tablet_entry.add_argument("file", help="Tablet file path")
    tablet_entry.add_argument("path", help="File path for the entry")
    tablet_entry.add_argument("--diff", help="Diff content")
    tablet_entry.add_argument("--diff-file", help="Path to diff file")
    tablet_entry.add_argument("--notes", help="Notes (can be JSON)")
    tablet_entry.set_defaults(func=cmd_tablet_add_entry)
    
    # Inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect any file")
    inspect_parser.add_argument("file", help="File to inspect")
    inspect_parser.set_defaults(func=cmd_inspect)
    
    # Sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List all saved sessions")
    sessions_parser.add_argument("--dir", default="./sessions", help="Sessions directory (default: ./sessions)")
    sessions_parser.set_defaults(func=cmd_sessions_list)
    
    # View command
    view_parser = subparsers.add_parser("view", help="View session file details")
    view_parser.add_argument("file", help="Session file path (.auratab or .auractx)")
    view_parser.set_defaults(func=cmd_view_file)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.command == "capsule":
            capsule_parser.print_help()
        elif args.command == "tablet":
            tablet_parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
