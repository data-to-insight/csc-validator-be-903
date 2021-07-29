import json
import requests

# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
USERNAME = '<your-username>'
PASSWORD = '<your-github-token-here>'

# The repository to add this issue to
REPO_OWNER = 'SocialFinanceDigitalLabs'
REPO_NAME = 'quality-lac-data-beta-validator'

def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    # Create an authenticated session to create the issue
    session = requests.session()
    session.auth=(USERNAME, PASSWORD)
    # Create our issue
    issue = {'title': title,
             'body': body,
             'assignee': assignee,
             'milestone': milestone,
             'labels': labels}
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


import pandas as pd

df = pd.read_csv('issues.csv')

print(df.columns)
for issue in df.itertuples():
    title = f'Error code {issue.Error} - {issue.Message}'
    body = (
        f'## Error information\n'
        f'#### Error code\n'
        f'{issue.Error}\n'
        f'#### Description to display\n'
        f'{issue.Message}\n'
        f'#### DfE Long-form description of error\n'
        f'{issue.Reason}\n'
        f'#### DfE suggested coding\n'
        f'{issue.Coding}\n\n\n'
        f'For further info, refer to the DfE validation document [here](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/974999/Children_looked_after_data_collection_2020_to_2021_validation_checks_-_version_1.3.pdf) '
    )
    labels = ['validation-rule', issue.Label]
    make_github_issue(title, body=body, labels=labels)