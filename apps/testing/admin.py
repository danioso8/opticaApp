"""
Admin para Testing App
"""
from django.contrib import admin
from .models import TestBot, TestRun, TestResult


@admin.register(TestBot)
class TestBotAdmin(admin.ModelAdmin):
    list_display = ['name', 'test_type', 'organization', 'frequency', 'is_active', 'status', 'last_run']
    list_filter = ['test_type', 'frequency', 'is_active', 'status']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_run', 'total_tests', 'passed_tests', 'failed_tests']


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_display = ['test_bot', 'started_at', 'completed_at', 'status', 'errors_found']
    list_filter = ['status', 'started_at']
    readonly_fields = ['started_at', 'completed_at', 'execution_log', 'results']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_run', 'url', 'method', 'success', 'status_code', 'response_time', 'tested_at']
    list_filter = ['success', 'method', 'tested_at']
    search_fields = ['url', 'error_message']
    readonly_fields = ['tested_at']
