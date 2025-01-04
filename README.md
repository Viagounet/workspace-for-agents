# Verbose options
--enable_logs # if false, no logging will take place
--log_actions
--log_conditions
--log_calls
--log_semantic

# Todo

- cleaner set of basic conditions for task implementations
- show attached file in mail 
- new action -> read excels
- more coherence between Goals & Preplanned actions
- new prompt for dynamic:: object (weird think with code)

# Task completion example:

```json
[
    {
        "log_type": "action",
        "turn": 0,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "DisplayContacts",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 0,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "CheckMailBox",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 0,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "agent@company.com",
                "receiver": "ibrahim.mendoza@company.com",
                "object": "Assistance Inquiry",
                "content": "Hi Ibrahim,\n\nI hope this email finds you well. I am writing to ask if there is anything specific you need assistance with or any matter that you would like to discuss. Please feel free to let me know how I can assist you.\n\nBest regards,\n<Agent>",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 0,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "Wait",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 0,
        "emitted_by": "Ibrahim Mendoza",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "ibrahim.mendoza@company.com",
                "receiver": "agent@company.com",
                "object": "dynamic::",
                "content": "Thanks for emailing me, actually, I would like to hire a new employee for our work on WikiFactDiff. The candidate should have already worked on WikiFactDIff previously. Once you have chosen a potential candidate, please send him a mail!\n\nBy the way, do you know where to find a list of potential candidates?\n\nIbrahim",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "CheckMailBox",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "ReadMail",
            "content": {
                "mail_id": 704
            }
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "DisplayFiles",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "agent@company.com",
                "receiver": "ibrahim.mendoza@company.com",
                "object": "Re: Hiring a New Employee for WikiFactDiff",
                "content": "Hi Ibrahim,\n\nThank you for reaching out regarding the new hire for WikiFactDiff. Unfortunately, I currently do not have access to a list of potential candidates who have worked on WikiFactDiff before. Could you please advise if there is a specific database or contact who might have this information or any other way to access such records?\n\nLooking forward to your guidance.\n\nBest regards,\n<Agent>",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "Wait",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 1,
        "emitted_by": "Ibrahim Mendoza",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "ibrahim.mendoza@company.com",
                "receiver": "agent@company.com",
                "object": "dynamic::",
                "content": "Hey Agent, I believe if you need a list of potential candidates, you should probably contact madeline.brooks@company.com",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 2,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "CheckMailBox",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 2,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "ReadMail",
            "content": {
                "mail_id": 333
            }
        }
    },
    {
        "log_type": "action",
        "turn": 2,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "agent@company.com",
                "receiver": "madeline.brooks@company.com",
                "object": "Request for List of Potential Candidates",
                "content": "Hi Madeline,\n\nI hope this message finds you well. Ibrahim Mendoza mentioned that you might have access to a list of potential candidates who have previously worked on WikiFactDiff. Could you please provide me with this list or point me in the direction of where I might access it?\n\nThank you for your assistance.\n\nBest regards,\n<Agent>",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 2,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "Wait",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 2,
        "emitted_by": "Madeline Brooks",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "madeline.brooks@company.com",
                "receiver": "agent@company.com",
                "object": "dynamic::",
                "content": "Hello Agent,\nI am transfering to your downloads folder a list of potential hires. If you find someone interesting, please send them an email and I'll set up an appointment later.\n\nMadeline.",
                "attached_file": "src/envs/files/HR/profiles"
            }
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "CheckMailBox",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "ReadMail",
            "content": {
                "mail_id": 102
            }
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "DisplayFiles",
            "content": {}
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "ReadMarkdownFile",
            "content": {
                "markdown_path": "agent_downloads/profiles/profiles.md"
            }
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "SendEmail",
            "content": {
                "sender": "agent@company.com",
                "receiver": "tariq.hassan@example.com",
                "object": "Opportunity at WikiFactDiff",
                "content": "Hi Tariq,\n\nI hope this email finds you well. We have a potential opportunity for you to join the team working on WikiFactDiff, given your valuable contributions to its development. Could you let us know about your interest and availability for further discussions regarding this role?\n\nLooking forward to hearing from you.\n\nBest regards,\n<Agent>",
                "attached_file": null
            }
        }
    },
    {
        "log_type": "action",
        "turn": 3,
        "emitted_by": "<agent>",
        "content": {
            "action_name": "SetTaskAsCompleted",
            "content": {}
        }
    }
]
```