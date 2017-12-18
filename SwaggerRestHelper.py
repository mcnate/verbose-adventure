import time
import csv
import github3

'''
Export all github issues and comments into the preferred csv format used by Jira import.
'''

# api settings for github
# add a token OR user and pass, not both
OAuth_token = ''
git_username = ''
git_password = ''

git_org = ''

# github user to jira user mappings
user_dict = {
#   "github_user"       : "jira_user"
    "johnDoe"            : "JDoe",
}

# csv name
csv_issues_name = "github_issues.csv"


def change_git_markup_to_jira_markup(text):
    text = text.replace('### ', 'h6.')
    text = text.replace('## ', 'h4.')
    text = text.replace('# ', 'h2.')
    text = text.replace('```', '{code}')
    text = text.replace('>', 'bq.')
    # replace github "@" mentions with jira "~" mention
    if "@" in text:
        for key in user_dict:
            text = text.replace("@" + key, "[~%s]" % user_dict[key])

    return text


def run_csv():
    """
    Export github issues into a csv format
    """
    with open(csv_issues_name, 'wb') as f:
        issues_csv = csv.writer(f, delimiter=b",", quoting=csv.QUOTE_MINIMAL)
        if OAuth_token:
            github = github3.login(token=OAuth_token)
        else:
            try:
                # Python 2
                prompt = raw_input
            except NameError:
                # Python 3
                prompt = input

            def my_two_factor_function():
                code = ''
                while not code:
                    # The user could accidentally press Enter before being ready,
                    # let's protect them from doing that.
                    code = prompt('Enter 2FA code: ')
                return code
            github = github3.login(username=git_username, password=git_password, two_factor_callback=my_two_factor_function)

        '''Uncomment to print out list of org members'''
        # for user in github.organization(git_org).members():
        #    print user.login

        # get the git issues and write the rows to the csv
        git_org_issues = github.search_issues("org:%s is:issue is:open" % git_org)
        labels_max_header_count = 0
        comment_max_header_count = 0
        for git_issue in git_org_issues:
            if len(git_issue.labels) > labels_max_header_count:
                labels_max_header_count = len(git_issue.labels)
            if git_issue.comments > comment_max_header_count:
                comment_max_header_count = git_issue.comments
        # csv issues headers
        jira_headers = [
            'Summary',
            'Description',
            'Status',
            'Reporter'
        ]
        label_headers = ['Labels'] * labels_max_header_count
        comment_headers = ['Comment'] * comment_max_header_count
        jira_headers.extend(label_headers)
        jira_headers.extend(comment_headers)

        # write header rows
        issues_csv.writerow(jira_headers)

        for git_issue in git_org_issues:
            labels = [''.encode('utf8')] * labels_max_header_count
            comments = [''.encode('utf8')] * comment_max_header_count
            if len(git_issue.labels):
                for index, git_label in enumerate(git_issue.issue.labels()):
                        labels[index] = git_label.name
                        labels[index] = labels[index].encode('utf8')
            if git_issue.comments:
                for index, git_comment in enumerate(git_issue.issue.comments()):
                    # Jira Format Example: "06/Sep/17 10:00 AM;test-user;This is a comment"
                    comment_body = change_git_markup_to_jira_markup(git_comment.body)
                    comments[index] = u';'.join((git_comment.created_at.strftime('%d/%b/%y %I:%M %p'),
                                                 user_dict[git_comment.user.login],
                                                 comment_body))
                    comments[index] = comments[index].encode('utf8')
            issue_body = change_git_markup_to_jira_markup(git_issue.body)
            issue = [
                git_issue.title.encode('utf8'),
                issue_body.encode('utf8'),
                git_issue.state.encode('utf8'),
                user_dict[git_issue.issue.user.login].encode('utf8'),
            ]
            issue.extend(labels)
            issue.extend(comments)
            issues_csv.writerow(issue)
            print(issue[0])
            time.sleep(1)


if __name__ == '__main__':
    run_csv()
