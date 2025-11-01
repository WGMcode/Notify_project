WGM
Safety and reproducibility checked independetly and verfied on 3 different LLMs
Date: 2025-10-01
--- Script to send email notifications on script completion or failure
Follow these steps to use:
1. Set the following environment variables in your system by opening the settings.json file (Ctrl+Shift+P -> Preferences: Open User Settings (JSON)):
   Paste the following, replacing placeholders with your actual email credentials:
   {...some existing settings...,
    "terminal.integrated.env.windows": {
        "EMAIL_USER": "gmail address you want to send from",
        "EMAIL_PASS": "app password you generated from gmail (go to google account -> security -> app passwords (need 2-step verification enabled))",
        "EMAIL_TO": "gmail address you want to send to"
    }
   }
2. At the top of any Python script you want this functionality to apply to (inside the same folder), add:
   import notify_on_finish
   notify_on_finish.setup()
3. Close and reopen VSCode to ensure environment variables are loaded.
4. Daar vat hy. Run your script as usual. You will receive an email when it finishes or crashes.
--- EXTRAS ---
Set line 36 to False if you don't want to save and send the complete terminal output and only want a brief email notification on finish/failure.

