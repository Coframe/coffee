# Coffee ☕

— <ins>**Cof**</ins>rame <ins>**F**</ins>ront-<ins>**E**</ins>nd <ins>**E**</ins>ngineer

Build a frontend with prompting.

https://private-user-images.githubusercontent.com/25165841/280459550-e8c1ee7e-68a1-4e90-bbdf-4ff295db4d55.mp4

App is rendered out on the frontend. On top of this frontend is the coframe copilot, which is like the editor. As you prompt, the page updates in realtime. You can select parts of the page to refine. It should output some type of organization for API consumption expectation, and create a system for mocks where it expects APIs to come from. It should know how to route to different parts of the filesystem based on how we prompt it.

### How to run
```
docker-compose build
docker-compose up
```
4. Install chrome extension from the `coffee/extension` folder.


Arch:

- Default boilerplate next app with hot reload.
- Separate python service that’s modifying the FE app and contains the prompts.
- Chrome extension that allows for element selection.
- Use git to roll back to previous state and show it.
    - Should be able to see screenshots of prev versions in the extension or somewhere

Opinions:

- Everything should be labeled with element IDs that are intuitive so that the selector can notify the LLM about what’s selected and needs to be edited.
- Rail system? Files have who they depend on and who depends on them?
- Data expectations from backend - each time there’s something that calls data from the backend, the data expectation is written down and tagged in a YAML file using OpenAPI and an example is provided (more can be generated upon request). Example provided in the form of json in MockAPIs folder?
    - Should be able to mock and try out new API inputs
- Files should be no more than 8k tokens. If feature creep happens, break up into components.
- File system needs to be well-organized and in line with what GPT-4 is good at.

AI:

- We need quite a robust directory reasoning system and navigation / charter system. This overhead could make up as much as half of the prompts and “code”.
- Files should be small.
- When refining, give it the context it needs. If it’s a design thing, can be done in place. If something larger, look at dependencies.
- Put description at top of file in comments section in such a way where AI can ingest just that and see if it makes sense to mess with it or not.
- Should have threads that have all context like a chat, and be able to spin up branch-off jobs that tell it what it needs in separate ones, and the output is brought back in without the branch job filling up extra context (like an agent)
    - Example: In page.tsx, I’ve changed a variable name from abc to xyz. component.tsx exports Component which is implemented in page.tsx and takes in abc. I want to go see where in component.tsx abc is implemented and change its name to xyz without that clogging up the context of the thread.
- It should debug itself, iteratively.

Structure:

- Should have a “directory” which tells it where the component associated with an element id (as selected by user) is
- Should have a description at the top of each file that does […]
- Branch jobs: at any point, the AI should be able to spin off a branch that does something and inserts the output back into the current thread without including the work done in that branch in the main thread. This could be something like identifying and pasting a relevant function from another file into the next prompt for context.

~ Build a frontend as cheap as a cup of coffee, and in the time it takes to drink it ~

