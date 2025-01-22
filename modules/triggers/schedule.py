"""
Scheduled Trigger Module

Provides a time-based trigger implementation for workflows using both cron-style
and interval-based scheduling. Inherits from BaseTrigger to provide consistent
trigger behavior across different trigger types.

Classes:
    ScheduledTrigger: Executes workflows based on time-based schedules using
                      either cron expressions or fixed intervals.

Dependencies:
    schedule: For scheduling logic and job management
    threading: For background schedule monitoring

Example Usage:
    # Run every 5 minutes
    trigger = ScheduledTrigger(
        workflow=my_workflow.execute,
        interval=5,
        interval_unit='minutes'
    )
    trigger.start()

    # Daily at 3:30 PM
    trigger = ScheduledTrigger(
        workflow=my_workflow.execute,
        cron_expression='30 15 * * *'
    )
    trigger.start()

Note:
    The scheduler runs in a daemon thread. Ensure the main thread remains alive
    while scheduling is active. For cron expressions, only the first two fields
    (minute and hour) are currently utilized for daily scheduling.
"""

import time
import schedule
from datetime import datetime
from typing import Callable, Any
import threading
from modules.triggers.base_trigger import BaseTrigger

class ScheduledTrigger(BaseTrigger):
    """
    Time-based workflow trigger supporting cron-style and interval scheduling.

    This trigger implementation uses the schedule library to manage recurring
    jobs and executes associated workflows when scheduled times occur.

    Attributes:
        cron_expression (str): Optional cron-style schedule string (min hour * * *)
        interval (int): Recurring interval value
        interval_unit (str): Time unit for intervals (seconds|minutes|hours|days)
        scheduler (schedule.Scheduler): Underlying scheduler instance
        _active (bool): Flag indicating if trigger monitoring is active

    Args:
        workflow (Callable[[], Any]): Workflow function to execute when triggered
        cron_expression (str): Cron string in 'min hour * * *' format
        interval (int): Recurring interval length
        interval_unit (str): Time unit for intervals (default: minutes)

    Raises:
        ValueError: For invalid cron expressions or scheduling parameters
    """
    def __init__(
        self,
        workflow: Callable[[], Any],
        cron_expression: str = None,
        interval: int = None,
        interval_unit: str = 'minutes'
    ):
        super().__init__(workflow)
        self.cron_expression = cron_expression
        self.interval = interval
        self.interval_unit = interval_unit
        self.scheduler = schedule.Scheduler()

        if cron_expression:
            self._parse_cron(cron_expression)
        elif interval:
            self._setup_interval()

    def _parse_cron(self, cron: str):
        """Parse cron-style expression (min hour day month day_of_week)"""
        parts = cron.split()
        if len(parts) < 2:
            raise ValueError("Invalid cron expression")
        # Schedule daily at specific time (minute, hour)
        self.scheduler.every().day.at(f"{parts[1]}:{parts[0]}").do(self.execute_workflow)

    def _setup_interval(self):
        """Correct interval-based scheduling"""
        job = self.scheduler.every(self.interval)
        getattr(job, self.interval_unit).do(self.execute_workflow)

    def check_condition(self) -> bool:
        return len(self.scheduler.get_jobs()) > 0

    def start(self):
        self._active = True
        def run_scheduler():
            while self._active:
                self.scheduler.run_pending()
                time.sleep(1)

        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()