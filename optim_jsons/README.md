# Optimized JSON Data Structure

This folder contains normalized JSON files for DHS 2025 event data.

## Files

### 📄 `sessions.json` (75 KB)
Contains all session information including:
- Session title, type (Keynote, Hack Session, PowerTalk, Hack Panel)
- Speaker details (name, designation)
- Session description
- Session URL
- **Day information** (day, day_number, day_date, time, location) - for 15 scheduled sessions
- 46 sessions are not yet scheduled (no day information)

**Total:** 61 sessions (15 scheduled, 46 unscheduled)

### 📄 `speakers.json` (88 KB)
Contains all speaker profiles including:
- Name, designation, company
- Biography
- LinkedIn profile
- Associated sessions
- Profile URL and slug

**Total:** 74 speakers

### 📄 `workshops.json` (44 KB)
Contains all workshop information including:
- Title, instructor details
- Description, date, time, venue
- Module breakdown with content

**Total:** 10 workshops

## Benefits of This Structure

✅ **No Redundancy** - Each piece of data exists in exactly one place  
✅ **Modularity** - Load only the data you need  
✅ **Easier Updates** - Modify sessions, speakers, or workshops independently  
✅ **Smaller Files** - Faster loading and better performance  
✅ **Programmatic Views** - Generate agenda/day-wise views on demand

## Generating Day-Wise Agenda

Instead of storing agenda data separately, generate it programmatically when needed:

```python
# Use the provided utility script
python generate_agenda.py
```

Or in your application:

```python
import json

# Load sessions
with open('optim_jsons/sessions.json', 'r') as f:
    data = json.load(f)
    sessions = data['sessions']

# Group by day (implement your logic)
agenda = {}
for session in sessions:
    day = session.get('day', 'Day 1')
    if day not in agenda:
        agenda[day] = []
    agenda[day].append(session)
```

## Usage in Applications

```python
import json
from pathlib import Path

# Load specific data as needed
def load_sessions():
    with open('optim_jsons/sessions.json', 'r') as f:
        return json.load(f)['sessions']

def load_speakers():
    with open('optim_jsons/speakers.json', 'r') as f:
        return json.load(f)['speakers']

def load_workshops():
    with open('optim_jsons/workshops.json', 'r') as f:
        return json.load(f)['workshops']

# Example: Get all keynote sessions
sessions = load_sessions()
keynotes = [s for s in sessions if s['type'] == 'Keynote']

# Example: Find speaker by name
speakers = load_speakers()
speaker = next((s for s in speakers if s['name'] == 'Pratyush Kumar'), None)
```

## Data Relationships

- **Sessions** reference speakers by name and designation
- **Speakers** list their associated sessions
- **Workshops** are independent entities

When you need to link data (e.g., get full speaker details for a session), perform the lookup programmatically rather than duplicating the data.
