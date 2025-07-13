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

Step 2: Prompts to arrive at the code
1. Build an agent using agent development kit that will take a requirement and generate the working code
2. Add a method to the agent to automatically generate unit tests for the code it creates. also use gemini model instead of openai model
3. How can I make the agent save the generated code and tests to separate files?
4. Modify the agent to automatically run the generated tests using pytest and report the results.
5. Add a step where the agent attempts to fix the code if the initial tests fail.
6. How can I add logging to a file to track the agent's entire process for each requirement?
7. An error occurred while communicating with the Google AI API: 404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.
