import sys
import os
import json
from datetime import datetime, timedelta
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.task_scheduler import TaskSchedulerTool

def test_task_scheduler_initialization():
    """Test that the TaskSchedulerTool initializes correctly."""
    scheduler = TaskSchedulerTool()
    assert scheduler is not None, "TaskSchedulerTool should be initialized"

def test_schedule_task_with_absolute_date():
    """Test scheduling a task with an absolute date."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Schedule a task
    result = scheduler.execute(
        operation="schedule", 
        title="Test Absolute Task", 
        due_date="2025-12-31"
    )
    
    assert "Task scheduled successfully" in result
    assert len(scheduler.tasks) == 1
    assert scheduler.tasks[0]['title'] == "Test Absolute Task"
    assert scheduler.tasks[0]['due_date'].startswith("2025-12-31")

def test_schedule_task_with_relative_date():
    """Test scheduling a task with a relative date."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Schedule a task
    result = scheduler.execute(
        operation="schedule", 
        title="Test Relative Task", 
        due_date="in 3 days"
    )
    
    assert "Task scheduled successfully" in result
    assert len(scheduler.tasks) == 1
    assert scheduler.tasks[0]['title'] == "Test Relative Task"
    
    # Check that the due date is approximately 3 days from now
    due_date = datetime.fromisoformat(scheduler.tasks[0]['due_date'])
    assert (due_date - datetime.now()).days == 3

def test_prevent_duplicate_tasks():
    """Test that duplicate tasks are prevented."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Schedule the same task multiple times
    results = []
    for _ in range(5):
        result = scheduler.execute(
            operation="schedule", 
            title="Duplicate Task", 
            due_date="2025-12-31"
        )
        results.append(result)
    
    # Verify only one task was added
    assert len(scheduler.tasks) == 1
    
    # Verify task IDs remain consistent
    assert all("Task scheduled successfully" in r for r in results)
    assert all(task['id'] == 1 for task in scheduler.tasks)

def test_task_list_and_filtering():
    """Test listing tasks with different filters."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Add multiple tasks
    scheduler.execute(operation="schedule", title="High Priority Task", due_date="2025-01-01", priority="high")
    scheduler.execute(operation="schedule", title="Medium Priority Task", due_date="2025-02-01", priority="medium")
    scheduler.execute(operation="schedule", title="Low Priority Task", due_date="2025-03-01", priority="low")
    
    # List all tasks
    list_result = scheduler.execute(operation="list", status="all")
    assert "High Priority Task" in list_result
    assert "Medium Priority Task" in list_result
    assert "Low Priority Task" in list_result
    
    # List only high priority tasks
    list_high_result = scheduler.execute(operation="list", status="pending")
    assert "High Priority Task" in list_high_result
    assert "Medium Priority Task" in list_high_result
    assert "Low Priority Task" in list_high_result

def test_task_completion():
    """Test marking tasks as complete."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Schedule a task
    scheduler.execute(operation="schedule", title="Task to Complete", due_date="2025-12-31")
    
    # Complete the task
    complete_result = scheduler.execute(operation="complete", task_id=1)
    
    assert "Task 1 'Task to Complete' marked as completed" in complete_result
    
    # Verify task status changed
    completed_tasks = [task for task in scheduler.tasks if task['status'] == 'completed']
    assert len(completed_tasks) == 1
    assert completed_tasks[0]['title'] == "Task to Complete"

def test_overdue_tasks():
    """Test listing overdue tasks."""
    scheduler = TaskSchedulerTool("test_tasks.json")
    
    # Clear existing tasks
    scheduler.tasks = []
    
    # Schedule an overdue task (set to a past date)
    past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    scheduler.execute(operation="schedule", title="Overdue Task", due_date=past_date)
    
    # Get overdue tasks
    overdue_result = scheduler.execute(operation="overdue")
    
    assert "Overdue tasks" in overdue_result
    assert "Overdue Task" in overdue_result

def main():
    """Run all tests and print results."""
    test_functions = [
        test_task_scheduler_initialization,
        test_schedule_task_with_absolute_date,
        test_schedule_task_with_relative_date,
        test_prevent_duplicate_tasks,
        test_task_list_and_filtering,
        test_task_completion,
        test_overdue_tasks
    ]
    
    passed = 0
    failed = 0
    
    for test in test_functions:
        try:
            test()
            print(f"✅ {test.__name__} PASSED")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\nTest Summary: {passed} Passed, {failed} Failed")
    return passed, failed

if __name__ == "__main__":
    total_passed, total_failed = main()
    sys.exit(total_failed)