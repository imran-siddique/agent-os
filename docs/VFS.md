# Virtual File System (VFS)

## Overview

The Virtual File System (VFS) is a lightweight in-memory file system designed for multi-agent SDLC collaboration. It maintains project state that all agents can share, allowing Agent A to see Agent B's edits in real-time.

## Why VFS?

SDLC agents don't just chat—they edit files. Traditional approaches where each agent has its own isolated file view lead to:

- **Inconsistency**: Agents have different views of the project
- **Lost work**: Edits by one agent aren't visible to others
- **No history**: Can't track who changed what and when
- **Coordination overhead**: Manual synchronization required

The VFS solves these problems by providing a **shared, versioned file system** that all agents access.

## Key Features

### 1. Shared Project State
All agents work on the same VFS instance, seeing changes immediately:

```python
from caas import VirtualFileSystem

# Create shared VFS
vfs = VirtualFileSystem()

# Agent 1 creates a file
vfs.create_file("/project/main.py", "print('hello')", agent_id="agent-1")

# Agent 2 can immediately read it
content = vfs.read_file("/project/main.py")  # "print('hello')"
```

### 2. Edit History Tracking
Every change is tracked with agent ID, timestamp, and optional message:

```python
# Agent 2 updates the file
vfs.update_file(
    "/project/main.py",
    "print('world')",
    agent_id="agent-2",
    message="Changed greeting"
)

# View complete history
history = vfs.get_file_history("/project/main.py")
for edit in history:
    print(f"{edit.agent_id} at {edit.timestamp}: {edit.message}")
```

### 3. Directory Support
Automatic parent directory creation and tree structure:

```python
# No need to create directories manually
vfs.create_file("/deep/nested/path/file.txt", "content", "agent-1")

# List directory contents
files = vfs.list_files("/deep", recursive=True)
```

### 4. Path Normalization
Consistent path handling across agents:

```python
# These all refer to the same file
vfs.read_file("/project/file.txt")
vfs.read_file("project/file.txt")
vfs.read_file("//project//file.txt")
```

### 5. Optional Persistence
Save/load VFS state to/from disk:

```python
# VFS with persistence
vfs = VirtualFileSystem(storage_path="/tmp/vfs_state.json")

# Changes are automatically saved
vfs.create_file("/data.txt", "content", "agent-1")

# Load on next initialization
vfs2 = VirtualFileSystem(storage_path="/tmp/vfs_state.json")
# File is already there
```

## API Reference

### Core Operations

#### Create File
```python
file_node = vfs.create_file(
    path="/project/main.py",
    content="print('hello')",
    agent_id="agent-1",
    metadata={"language": "python"}
)
```

**Parameters:**
- `path` (str): File path (normalized automatically)
- `content` (str): Initial file content
- `agent_id` (str): ID of agent creating the file
- `metadata` (dict, optional): Additional metadata

**Returns:** `FileNode` object

**Raises:**
- `ValueError`: If file already exists

#### Read File
```python
content = vfs.read_file("/project/main.py")
```

**Parameters:**
- `path` (str): File path to read

**Returns:** File content as string

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If path is a directory

#### Update File
```python
file_node = vfs.update_file(
    path="/project/main.py",
    content="print('world')",
    agent_id="agent-2",
    message="Update greeting"
)
```

**Parameters:**
- `path` (str): File path to update
- `content` (str): New content
- `agent_id` (str): ID of agent making update
- `message` (str, optional): Commit-like message

**Returns:** Updated `FileNode` object

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If path is a directory

#### Delete File
```python
result = vfs.delete_file("/project/main.py", agent_id="agent-1")
```

**Parameters:**
- `path` (str): File path to delete
- `agent_id` (str): ID of agent deleting file

**Returns:** `True` if successful

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If directory is not empty

#### List Files
```python
files = vfs.list_files("/project", recursive=True)
```

**Parameters:**
- `path` (str): Directory path
- `recursive` (bool): Include subdirectories

**Returns:** `FileListResponse` with list of files

#### Get File History
```python
history = vfs.get_file_history("/project/main.py")
```

**Parameters:**
- `path` (str): File path

**Returns:** List of `FileEdit` objects

## REST API Endpoints

The VFS is also exposed via REST API:

### POST /vfs/files
Create a new file

**Request body:**
```json
{
  "path": "/project/main.py",
  "content": "print('hello')",
  "agent_id": "agent-1",
  "metadata": {"language": "python"}
}
```

### GET /vfs/files?path=/project/main.py
Read a file

### PUT /vfs/files
Update a file

**Request body:**
```json
{
  "path": "/project/main.py",
  "content": "print('world')",
  "agent_id": "agent-2",
  "message": "Update greeting"
}
```

### DELETE /vfs/files?path=/project/main.py&agent_id=agent-1
Delete a file

### GET /vfs/list?path=/project&recursive=true
List files in directory

### GET /vfs/history?path=/project/main.py
Get file edit history

### GET /vfs/state
Get complete VFS state

## Multi-Agent Example

See `examples/multi_agent/vfs_collaboration.py` for a complete example showing:

- **Developer Agent**: Creates initial code
- **Reviewer Agent**: Reviews and improves code
- **Documenter Agent**: Adds documentation
- **Tester Agent**: Creates tests

All agents work on the shared VFS, demonstrating real multi-agent collaboration.

## Use Cases

### 1. Collaborative Code Generation
Multiple agents work together to build a complete application:
- One agent writes the main logic
- Another adds error handling
- A third writes tests
- A fourth adds documentation

### 2. Code Review Workflows
- Developer agent creates initial code
- Reviewer agent reads and suggests improvements
- Developer agent applies changes
- All changes tracked in history

### 3. Documentation Generation
- Agents read code from VFS
- Generate documentation based on actual code
- Other agents can reference the documentation

### 4. Test Generation
- Test generation agents read production code
- Create corresponding test files
- Integration test agents verify tests work

## Design Principles

1. **Simplicity**: In-memory dict-based structure, no complex database
2. **Consistency**: All agents see the same state immediately
3. **Auditability**: Complete edit history for all files
4. **Performance**: Fast in-memory operations
5. **Optional Persistence**: Save/load state when needed

## Limitations

- **In-memory only**: Primary storage is in-memory (can be persisted)
- **No locking**: Assumes cooperative agents (no concurrent edit conflicts)
- **No branches**: Single linear history per file
- **Not a Git replacement**: Designed for agent collaboration, not version control

## Future Enhancements

Potential future additions:
- **Git backend**: Use actual Git repository as storage
- **Conflict resolution**: Handle concurrent edits
- **Branching**: Support multiple versions
- **File watching**: Notify agents of changes
- **Search**: Full-text search across files

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## License

MIT License - see `LICENSE` file for details.
