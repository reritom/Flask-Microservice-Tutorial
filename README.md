# Creating a multi-microservice application deployed using docker-compose

Typically I skip any guide that requires me to make external accounts or has any propriety dependencies, so this guide doesn’t require any of that, and the end result will be deployed on local, so no need to worry about making trial accounts with cloud hosts.

This guide will consider the development of a system comprised of multiple intercommunicating microservices. The stack of this application is one of personal preference, but there are any number of different variations, so check out the stack below before we go into further detail.

### Stack used in this guide:
- Flask backends (But you could use NodeJS with express)
SQLite3 with flask sqlalchemy
- VueJS frontend (React is another popular choice)
- Docker
- Docker-compose
- Postman

### Prerequisites:
- A python environment handler, because we will create multiple environments. I use conda, but you could also using something like venv or poetry.
- You need to have docker installed (add link), this guide won’t cover that process because the docker documentation is very complete.
- You’ll need NodeJS and npm
- Some knowledge of Flask apps, sql orms, NodeJS, VueJS. In a lot of cases I will go through examples assuming some prior knowledge, but in those cases I will link to external resources that cover them in more detail if relevant.

### Terminology:

Having started writing this, I realised that I quickly start using terms which may mean different things to different people, so I will clarify terminology before we continue.

- Client: The end-user who consumes the UI in their browser
- API Client: Anything which consumes an API (internal or external)
- Backend: A backend is any system which exposes an API to be consumed. It could be a simple Flask app, or an express app, or any many other things which aren’t necessarily HTTP servers.
- Application: An application is a collection of backends which work together.
- Frontend: A system which handles the direct client interactions, so this covers the UI of the webpage, which could either be presented as a SPA (single page application) or as an express app which renders html server-side.
- Component: Backends and Frontends can both be considered as Components. Components are standalone and should be tested/testable by themselves.

## When would we need to make an application like this?

What we intend to make is a full stack application. Typically one can find guides showing someone how to make any individual section of this guide, and typically they would use a different stack including more javascript based backends, or using databases like dynamo or redis (which can be used as a database).

## Context

Recently I was working on a large multi component application built with many flask micro services and found difficulties throughout where even in-depth google searches couldn’t guide me to the correct answer. At the time I wasn’t considering writing a guide about it, so I didn’t make note of most of these issues, but this guide will hopefully cover all the things I wish I could have found more easily.

## What will we make?

Well, let's cover a full stack scenario. This means we want a frontend that handles interactions with the user, including rendering the webpages in a simple and pretty way. We want a backend that handles any business logic. The backend will handle database interactions and any external API integrations.

For the purpose of this guide, we will make a simple inventory management system. Really this could be done with just a frontend and a single backend component, but we will add some additional steps to give wider coverage. I have chosen this project as it was something that developed out of the larger project I was working on and thought it would work well exposition-ally.

The additional step will be an API gateway backend which is a sort of router and authoriser of the client requests. This means our ‘application’ will consist of two backend components, one being the inventory manager, and one being the api gateway, and there will also be a frontend component. The application will expose a RESTful interface (we will get to this) which is to be consumed by the frontend

What is the scope of the inventory management system?
In this system we consider that have resources which relate the physical items. The resources should be able to be allocated for arbitrary durations. In this case, we will only consider one type of resource, continuous resources.

Continuous resources are items that can be allocated for any duration, starting at any time, and ending at any time. An example of this could be a bookable self-driving car. It is a continuous resource because when it is booked for a journey, it be for any duration.

… timeline showing continuous resource allocations

The alternative is an interval resource, which would be something like a launchpad or a runway, which may have discrete defined intervals for when they can be booked. Note that in any case, there can’t be any overlap of the allocations made on a resource.

… timeline showing interval resource windows and allocations

The scope of our system is for handling the booking of three different type of continuous resource, the self-driving car, lorry, and truck.

We want to be able to register a new instance of each to represent when one has been added into circulation, and we want to be able to delete them to represent when they have been decommissioned.

For the UI, we want a simple interface that allows us to list each type of resource, add or delete instances of the resource, list the allocations, and add or delete allocations.

## System definition?
Before starting, we should define our system to some extent and define how we expect the user to be able interact with it. We do this using UML diagrams and sequence diagrams respectively.

### UML:

We can describe our system with the following diagram. It allow use to clearly visualise each component and the respective links between our components.

…

### Basic sequence diagram:

We can describe how the API client interacts with our system using the sequence diagram below. Note that any internal complexities are hidden, all we care about it how the API client interacts with the application

…

### Advanced sequence diagram:

From an internal development perspective it can be useful to see more information that doesn’t need to be exposed to the API client, we can do that with the following diagram

…

### Swagger:

We can define the interface of our application by creating a swagger definition. A swagger definition is a file or collection of files which define the endpoints, methods, content, and responses that can be expected by interacting with our application. Swagger definitions are then use by API client while they develop the integration between their component and the application. Swagger can also be used for validation of request content and even for auto-generation of code.

Our system is a basic CRUD (create, read, update, delete) app with some additional validations, so our applications swagger should be quite simple.

…

## Development:

We will start by developing the backend and we start with the central system, which is the inventory management application, and then work outwards. If you work is an agile team, you will know this is the wrong approach. What we are doing here is called ‘horizontal slicing’, when what you would do in an agile is ‘vertical slicing’.

Horizontal slicing -
Vertical slicing -

So while I acknowledge that this isn’t the optimum approach, it is a much easier way to handle development from a technical perspective.

So the development will goes a follows:

Inventory management flask app -> API gateway application -> Frontend

## Inventory Management App (InvSys):

Start by creating a new directory in our application directory, we will call it ‘invsys’, short for inventory system. ‘cd’ into this directory, because all development in this section will be done in invsys. You should create a new python environment for this component so it can be self contained with its own dependencies tracked.

This application is a Flask app which exposes an API for creating the resources (car, truck, lorry) and creating allocations for the instances.

So we create a file called application.py which we will use to create a function that will create our application. Why a function to create the app instead of just instantiating the app at module level? Well if we want a dynamic configuration, such as to create a test app or a production app, then it is helpful to be able to pass parameters or configs while creating the app. If we define the app at module level, without a function to create it, it is harder to handle dynamic configurations.

A dummy flask app could look like the following:
```python
# application.py

from flask import Flask, Response

def create_application(db_uri: str) -> Flask:
	app = Flask(__name__)

	app.route(‘/‘)
	def dummy():
		return Response(‘This is InvSys’)

if __name__==“__main__”:
	app.run(host=“127.0.0.1”, port=5000, debug=True)
```

Before running this, you’ll notice that we import the flask module, so in your new python environment for invsys, running ‘pip install flask’, else you will get an ImportError like “ImportError: No module named flask”

If you run this using ‘python application.py’, you should now be able to put ‘127.0.0.1:5000’ in your browser and see ‘This is InvSys’.

By installing flask we have added a dependency to this component, and as it should be self contained and reproducible with a consistent dependency, we should track this dependancy. We will do this by making a ‘requirements.txt’ file which will list each dependancy and their version. While this can be made manually, we will cheat by running the command ‘pip freeze > requirements.txt’, which will list all the dependencies (in your hopefully clean python environment) and put them into requirements.txt file.
