# heycg_project/dashboard.py
from grappelli.dashboard import modules, Dashboard
from django.urls import reverse

class CustomIndexDashboard(Dashboard):
    
    def init_with_context(self, context):
        # Site Information
        self.children.append(modules.LinkList(
            title='HEYCG Portal',
            column=1,
            children=[
                {'title': 'View Website', 'url': '/', 'external': True},
                {'title': 'Member Dashboard', 'url': '/members/dashboard/', 'external': True},
                {'title': 'Donations', 'url': '/donation/', 'external': True},
            ]
        ))
        
        # User Management
        self.children.append(modules.ModelList(
            title='User Management',
            column=1,
            models=('django.contrib.auth.models.*',)
        ))
        
        # Website Management
        self.children.append(modules.ModelList(
            title='Website Management',
            column=2,
            models=('website.models.*',)
        ))
        
        # Membership Management
        self.children.append(modules.ModelList(
            title='Membership Management',
            column=2,
            models=('accounts.models.*', 'members.models.*')
        ))
        
        # Recent Actions
        self.children.append(modules.RecentActions(
            title='Recent Actions',
            column=3,
            limit=10
        ))