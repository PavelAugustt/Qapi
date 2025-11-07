Architecture Design(It's very messy)

---

features:
inf context where llm dynamically loads memory and compartmentalizes it. it’ll do its best to serve the user and live only for their benefit or it’ll be taken down.
cli tool to interact with it (instruct is basically the interaction command or send prompt command).
windows reminders of things to do.

---

## **1. (for memory, authentication, and cli commands, list it first)**

### **1. hashmaps or json objects (i think json objs make more sense)**

1. user goals map (list of goals) → (truncated desc), id, timestamp, entrydate, duedate, duetimeincomputertime
2. agent context (information about agent and its memories) (list of memories) → (truncated desc for ref), id, timestamp, entrydate
3. user context (information about user and its memories) (list of memories) → (truncated desc for reference), id, timestamp, entrydate
4. agent tasks (information about tasks to do for agent) (list of tasks) → (truncated desc for reference), id, timestamp, entrydate, duedate

### **2. 3 hashmaps priorities (weekly priorities, monthly priorities, daily priorities)**

1. id (text that describes what the priority is) → (detailed data abt priority, why, how etc)
2. frequently priorities are loaded into goals to plan each date, the day before

### **3. timeheap, daily reminders heap (goals, timestamp)**

1. end of each day, goals are loaded in and used to plan the next day's time heap
2. when corresponding timestamp is about to be hit in 5 mins by computer clock we make a reminder

### **4. a chatlog (list of conversations meant to be fed into an llm as context)**

1. this will be updated everyday and stored somewhere else, in other words only one day's log will matter to the llm.

### **5. log.txt**

self-explanatory. every interaction with server, llm tasks, everything must be logged and explained.
llms will have no way of interacting with log other than writing a desc before each task and that being logged.

---

## **architecture**

1. central server hosted remote with our data all in one place, in like render or something for free
2. a reminder program that calls the central server frequently for updates on time heap (maybe like a socket connection?) or:

   * load just the time heap locally to this program and run reminders locally
   * latter is better because no internet required
   * but socket means more future possibilities
   * hybrid: at end of each day, at a specific time or during night, the llm will get the local program or establish a socket connection and then use socket to send the timeheap and get pending updates from local machine
   * alternative: local machine establishes the connection and then work from there
3. a cli tool that can be used to interact with the server

   * for now we use one command, an instruct command that'll communicate with the llm and send an instruction to it

---

## **endpoints and cli tool commands**

1. **/instruct** async (req(user request), res(llm response after executing request))
2. **/healthcheck**, current stats, tasks, what the llm is working on, if it's busy etc
3. **/search** ideally used to query all data tree-like so user can pick data obj and traverse it, but too complicated rn. we'll let llm query it *for* us and return that
4. **/load** for socket connection manually for any new local programs
5. **/login** only one set of credentials in the system, works both ways, cli stores it locally, okay because you're sole user
6. **/logout** removes the local program from allowed devices

---

# **2. data flow and typical workflow**

for each of the descs there will be handler funcs called **load** that'll ask the llm for a list of params.
in the system prompt we'll outline func and data structures.

whenever llm has a task to execute from instruct or something to do for itself:

* it'll load all datastores and memories
* by reading trunc things and deciding which ones it needs for context and planning
* once completed it'll make a plan of execution and execute it recursively until it calls the end/my work function
* each work or instruct starts from fresh memory and system prompt
* it'll load memories it thinks are relevant just like humans do, just more tediously

### **1. every single data store hashmap, json db, etc will need update functions**

* these will be handler funcs only available to llm
* param = json store location (ex: user-context), truncated desc, longer desc, due date
* id, current date, timestamp are set automatically

### **2. time stamp functions**

there will be functions for timestamp.
llm needs timestamp before anything.
doesn't have to call it each prompt — time will be automatically fed in with current date.

### **3. json memory_load**

one memory_load func that accepts a list param (names of json databases).
max length 4.
llm can load from that.

there will also be memory_append, memory_delete.

* load will load ids and truncated descs
* load_max_desc (id_of_obj, location) will load the detailed desc

### **4. planning**

recurring event at end of day:

* create new timeheap
* timeheaps are popped when time is hit
* when there's a task for agent:

  * agent executes by server calling /agent_execute
  * during this time outside requests go to cache
  * respond once agent ready
  * if meant for human, agent can ignore

when creating timeheap:

* review goals
* all 3 priorities tables
* current day's journal entry
* previous week's journal entries

### **5. for each instruct**

the current chatlog is loaded from cache so user and agent can talk during day.

### **6. log.txt logic**

every endpoint and agent_execute logs whatever the func is doing.
might be wasteful of tokens if we let agent do stuff by itself.

### **7. rest of logic**

within corresponding endpoints and agent_execute:
login logic in login
instruct logic in instruct
etc

handler funcs are only for the agent/llm to call (ensures modularity but not too much modularity).

### **8. instruct function & querying**

this is the most important part.

llm gets instruct:

* if it's simple convo where llm doesn’t need to do anything → call end
* if not → call /agent_execute with verbose prompt of what user or agent wants

binary response:

* true → agent_execute
* false → end

  * log or append to chatlog programmatically (not via llm)

### **9. agent_execute**

llm makes an action plan of data it thinks it needs.
system prompt outlines all handler functions, datastores, and how to interact with them.

llm decides what's relevant, then returns json or list:

* list of function calls and responses
* server loads those responses into llm
* llm uses update functions with params to update datastores
