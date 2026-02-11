#!/usr/bin/env python3
"""
Utility script to generate day-wise agenda views from normalized session data.
This demonstrates how to programmatically create agenda views without storing redundant data.
"""

import json
from collections import defaultdict
from pathlib import Path


def load_sessions():
    """Load sessions from the normalized sessions.json file."""
    sessions_file = Path(__file__).parent / 'sessions.json'
    with open(sessions_file, 'r') as f:
        data = json.load(f)
    return data['sessions']


def group_sessions_by_day(sessions):
    """
    Group sessions by day.
    
    Note: Only sessions with day information will be included.
    Sessions without scheduling info will be in a separate 'Unscheduled' category.
    """
    days = defaultdict(list)
    
    for session in sessions:
        day = session.get('day', 'Unscheduled')
        days[day].append({
            'title': session['title'],
            'type': session['type'],
            'speakers': session['speakers'],
            'time': session.get('time', 'TBA'),
            'location': session.get('location', 'TBA'),
            'url': session.get('url', '')
        })
    
    return dict(days)


def generate_agenda():
    """Generate a day-wise agenda from sessions data."""
    sessions = load_sessions()
    agenda = group_sessions_by_day(sessions)
    
    # Sort days (Day 1, Day 2, Day 3, etc.)
    def day_sort_key(day_name):
        if day_name == 'Unscheduled':
            return 999
        try:
            return int(day_name.split()[-1])
        except:
            return 0
    
    return {
        'days': [
            {
                'day': day_name,
                'session_count': len(day_sessions),
                'sessions': day_sessions
            }
            for day_name, day_sessions in sorted(agenda.items(), key=lambda x: day_sort_key(x[0]))
        ]
    }


def save_agenda(output_file='agenda_generated.json'):
    """Generate and save the agenda to a file."""
    agenda = generate_agenda()
    output_path = Path(__file__).parent / output_file
    
    with open(output_path, 'w') as f:
        json.dump(agenda, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated agenda saved to: {output_path}")
    print(f"   Total days: {len(agenda['days'])}")
    for day in agenda['days']:
        print(f"   - {day['day']}: {day['session_count']} sessions")


if __name__ == '__main__':
    # Example usage
    print("Generating day-wise agenda from normalized sessions data...")
    print()
    
    # Load sessions
    sessions = load_sessions()
    scheduled = [s for s in sessions if s.get('day') and s.get('day') != 'Unscheduled']
    unscheduled = [s for s in sessions if not s.get('day')]
    
    print(f"📊 Loaded {len(sessions)} total sessions")
    print(f"   ✅ Scheduled: {scheduled.__len__()} sessions")
    print(f"   ⏳ Unscheduled: {unscheduled.__len__()} sessions")
    print()
    
    # Generate agenda
    save_agenda()
    print()
    print("💡 Tip: The agenda is generated on-demand from sessions.json")
    print("   Update sessions.json to automatically update the agenda.")

