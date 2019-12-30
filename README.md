# Creating a multi-microservice application deployed using docker-compose

Typically I skip any guide that requires me to make external accounts or has any propriety dependencies, so this guide doesn’t require any of that, and the end result will be deployed on local, so no need to worry about making trial accounts with cloud hosts.

This guide will consider the development of a system comprised of multiple intercommunicating micro-services. The stack of this application is one of personal preference, but there are any number of different variations, so check out the stack below before we go into further detail.

### Stack used in this guide:
- Flask backends (But you could use NodeJS with express) using SQLite3 with flask SQL Alchemy
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

def create_application() -> Flask:
	app = Flask(__name__)

	app.route("/")
	def dummy():
		return Response("This is InvSys")

  return app

if __name__==“__main__”:
  app = create_application()
	app.run(host=“127.0.0.1”, port=5000, debug=True)
```

Before running this, you’ll notice that we import the flask module, so in your new python environment for invsys, running ‘pip install flask’, else you will get an ImportError like “ImportError: No module named flask”

If you run this using ‘python application.py’, you should now be able to put ‘127.0.0.1:5000’ in your browser and see ‘This is InvSys’.

By installing flask we have added a dependency to this component, and as it should be self contained and reproducible with a consistent dependency, we should track this dependancy. We will do this by making a ‘requirements.txt’ file which will list each dependancy and their version. While this can be made manually, we will cheat by running the command ‘pip freeze > requirements.txt’, which will list all the dependencies (in your hopefully clean python environment) and put them into requirements.txt file.

```
# requirements.txt

Flask==1.1.1
```

This dummy application by itself isn't very useful, so before we start developing the actual application, lets define it. We know that the purpose is have resources that can be allocated, with 3 different types of resources. For each resource type, we want the following endpoints (we're being RESTful to an extent):

- POST /{resource_type} - to create an instance of the resource
- GET /{resource_type} - to get all instances of a given resource type
- GET /{resource_type}/<resource_id> - get a specific instance
- DELETE /{resource_type}/<resource_id> - delete a specific instance of a resource
- POST /{resource_type}/<resource_id>/allocations - create an allocation for this resource instance
- GET /{resource_type}/<resource_id>/allocations - get all allocations for this resource instance
- GET /{resource_type}/<resource_id>/allocations/<allocation_id> - get a specific allocation
- DELETE /{resource_type}/<resource_id>/allocations/<allocation_id> - delete the allocation

Note: the resource_type is static, there are only 3 of them and there is no way to add more of them using this interface, while the resource_ids and allocation_ids are dynamic and can be created using this interface.

Now we could go ahead and add a url rule for each of these to to application like such:

```python
from flask import Flask, jsonify

def create_application() -> Flask:
	app = Flask(__name__)

	app.route("/<resource_type>", methods=['POST'])
	def create_resource_instance(resource_type):
    # Here we will create the resource instance
		return jsonify({}), 201

  # Continue making routes for all the other endpoint/method combinations
  ...

  return app
```

If we were to do this though, our applications.py file would become very large very quickly. Additionally, we'd then need some way to distinguish the flows for creating interval resources and continuous resources (if interval resources were to be added at some point). Instead we could make the application more modular by using Flask Blueprints. Blueprints allow us to better organise and split our application.

While there may be other ways, I would think the best way to split the blueprints would be one for interval resources, and one for continuous resources. So in this case we will only have one blueprint, just for the continuous resources, but it allows us to make the code more flexible for future development. This reason alone isn't enough for using the Blueprint, because in development you often hear that making code future proof can be a waste of time, so there is another reason we will get to.

So inside our invsys directory we will make a 'blueprints' directory with an '__init__.py', and make a file called 'continuous_resource_blueprint.py'.

At this point your overall project directory should resemble this:

```
.
└── invsys
    ├── application.py
    ├── requirements.txt
    ├── blueprints
        ├── __init__.py
        └── continuous_resource_blueprint.py
```

I will mention two ways of handling the Blueprint with regard to the 3 resource types.

First, we could just create a static Blueprint which has the resource type as a dynamic element in the url, then each route function will need to validate the resource type (perhaps using a decorator), it could look something like this:

```python
# blueprints/continuous_resource_blueprint.py

from flask import Blueprint, jsonify

blueprint = Blueprint('ContinuousResourceBlueprint', __name__)

@blueprint.route('/<resource_type>', methods=['POST'])
def create_continuous_resource(resource_type):
  # Create the resource somehow
  return jsonify({}), 201

# Do the same for all the other endpoints
...
```
And then in our application.py we would register the Blueprint like so:
```python
# application.py

from flask import Flask, jsonify
from blueprints.continuous_resource_blueprint import blueprint as continuous_resource_blueprint

def create_application() -> Flask:
	app = Flask(__name__)
  app.register_blueprint(continuous_resource_blueprint)
  return app
```
While this would work just fine, you'd need to somewhere define acceptable resource_types, either in the environment for flexibility, or in some config.

If we know that the resource types are unlikely to change, then it would be nice for them to be clearly stated in the application.py. One way to do that would be using creating Blueprints using a function which states the resource type using closures.

Before looking at the blueprint, if we look at the new applications.py file, it would look more like this:

```python
from flask import Flask
from blueprints.continuous_resource_blueprint import create_continuous_resource_blueprint

def create_app() -> Flask:
    app = Flask(__name__)

    # Register continuous resource blueprints
    app.register_blueprint(
        create_continuous_resource_blueprint(
            blueprint_name="CarsBlueprint", # The name, used by flask when using the url_for function
            resource_type="Car", # The resource type
            resource_prefix="cars" # The base of the url for this resource type
        )
    )

    # Then do the same for lorry and truck
    ...

    return app
```
The benefit of the above snippet is that by looking at my application.py one can clearly see that the application has a continuous resource of type Car with the base url of '/cars'.

In our continuous_resource_blueprint.py we would then implement something like this:
```python
from flask import Blueprint
import logging

logger = logging.getLogger(__name__) # We won't go into this in this guide

def create_continuous_resource_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str) -> Blueprint:
    """
    blueprint_name: name of the blueprint, used by Flask for routing
    resource_type: name of the specific type of interval resource, such as Car or Lorry
    resource_prefix: the plural resource to be used in the api endpoint, such as cars, resulting in "/cars"
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route(f'/{resource_prefix}', methods=["POST"])
    def create_resource():
        logger.info("Creating resource")
        return jsonify({}), 201

    @blueprint.route(f'/{resource_prefix}', methods=["GET"])
    def get_resources():
        """
        Get all the resources, not including allocations
        """
        logger.info("Getting resources")
        return jsonify({}), 201

    # We then do this for all the other endpoints we listed
    ...
```

So we have the general setup of the Flask app and the blueprints for handling our three continuous resources. You'll note that the above snippet isn't using the resource_type parameter for anything, and this is because we have been neglecting an essential part of this component.

### How and where do we store the resources and allocations?
Well, I said in the introduction that we were going to use SQLAlchemy, so that was a spoiler. We will store the allocations and resources in an SQLite3 database and use SQLAlchemy as an ORM for accessing the database. More specifically we will use flask-SQLAlchemy which you can install using 'pip install flask-SQLAlchemy', remember, you will need to update your requirements.txt file with this new dependancy.

As is typical in this guide, I will show you two ways to handle the database related logic, with the latter being my preferred approach in this scenario, but we will get to this shortly as there is some setup and common work that needs to be done first.

Firstly, how do we actually use and initialise the database?

--- talk about the db and db init all the in the application.py
--- mention the circular dependency problem
--- introduce database.py
--- create models directory
--- create each model

The common aspect will be the models. These are our
