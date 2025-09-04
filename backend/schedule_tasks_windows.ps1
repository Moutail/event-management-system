# Windows Task Scheduler helper for Django cron-like jobs
param(
    [string]$PythonPath = "python",
    [string]$ManagePy = "manage.py",
    [string]$ProjectDir = "."
)

function Register-DjangoTask($Name, $Args, $Trigger) {
    $action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$ManagePy $Args" -WorkingDirectory $ProjectDir
    Register-ScheduledTask -TaskName $Name -Action $action -Trigger $Trigger -RunLevel Highest -Force | Out-Null
    Write-Host "Task '$Name' registered"
}

# 24h reminders daily every 30 minutes
$trigger24 = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(1)
$trigger24.Repetition = (New-ScheduledTaskRepetitionSettings -Interval (New-TimeSpan -Minutes 30) -Duration ([TimeSpan]::MaxValue))
Register-DjangoTask -Name "EMS_SendVirtualReminders_24h" -Args "send_virtual_reminders --type 24h" -Trigger $trigger24

# 1h reminders every 10 minutes
$trigger1h = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(2)
$trigger1h.Repetition = (New-ScheduledTaskRepetitionSettings -Interval (New-TimeSpan -Minutes 10) -Duration ([TimeSpan]::MaxValue))
Register-DjangoTask -Name "EMS_SendVirtualReminders_1h" -Args "send_virtual_reminders --type 1h" -Trigger $trigger1h

# Waitlist processing every 5 minutes
$triggerWait = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(3)
$triggerWait.Repetition = (New-ScheduledTaskRepetitionSettings -Interval (New-TimeSpan -Minutes 5) -Duration ([TimeSpan]::MaxValue))
Register-DjangoTask -Name "EMS_ProcessVirtualWaitlist" -Args "process_virtual_waitlist" -Trigger $triggerWait

# Recording cleanup hourly
$triggerCleanup = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(4)
$triggerCleanup.Repetition = (New-ScheduledTaskRepetitionSettings -Interval (New-TimeSpan -Hours 1) -Duration ([TimeSpan]::MaxValue))
Register-DjangoTask -Name "EMS_CleanupVirtualRecordings" -Args "cleanup_virtual_recordings" -Trigger $triggerCleanup

Write-Host "All tasks registered. Open Task Scheduler to verify."
