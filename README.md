# SDLCAgent_CodeTestRunFixCode1

Vibe coding using Google Code Assist with VSCode IDE. 

Step 1: 

install IDE and plugin 
https://code.visualstudio.com/
https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist
Connect gmail id to the gemini code assist plugin and authorise 
In the left panel of VS Code IDE > gemini code assist with a ai icon > authorise your google id and following URL will auto open with message saying
https://developers.google.com/gemini-code-assist/auth/auth_success_gemini
“The authentication process has been successfully completed.. You can now close the current window and go back to your IDE. Gemini Code Assist, an AI tool, is now available for use. Gemini Code Assist can help you solve code problems, generate code, and provide inline suggestions.”
Developers can sign up with their personal Google account to access Gemini Code Assist available at no cost, no credit card needed. This version has high limits on operations such as code completions (6,000 per day), chat engagements (240 per day), and code reviews. 
Visual studio code (IDE) + Gemini code assist (Model) 

Step 2: 
Prompts to arrive at the code
1. Build an agent using agent development kit that will take a requirement and generate the working code
2. Add a method to the agent to automatically generate unit tests for the code it creates. also use gemini model instead of openai model
3. How can I make the agent save the generated code and tests to separate files?
4. Modify the agent to automatically run the generated tests using pytest and report the results.
5. Add a step where the agent attempts to fix the code if the initial tests fail.
6. How can I add logging to a file to track the agent's entire process for each requirement?
7. An error occurred while communicating with the Google AI API: 404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.

Step 3:
1. To get the GOOGLE_API_KEY 
https://aistudio.google.com/u/2/apikey -- 
https://ai.google.dev/gemini-api/docs/rate-limits
2. head to the directory of the code
3. create .env file with following line and update the api key obtained in earlier step
 ---- GOOGLE_API_KEY=' '  ---- 
4. create .gitignore file with
 ---- .env  ---- 
5. create virtual enbironment
 ---- python3 -m venv venv ---- 
6. Activate the virtual environment:  must do this every time there is work on the project in a new terminal session. notice the terminal prompt changes to show (venv)
 ---- source venv/bin/activate ---- 
7. Install dependencies
 ---- pip install -r requirements.txt ---- 
8. run the code
 ---- python SDLCAgent.py ---- 

Step 4:

Rate limit error when using free tier model 'gemini-1.5-pro-latest'

A critical error occurred: Google AI API call failed in generate_code: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. [violations {
}
violations {
}
violations {
}
, links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, retry_delay {
  seconds: 6
}
]
   
