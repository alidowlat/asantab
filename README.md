# AsanTab --- Influencer Advertisement Marketplace Platform

# AsanTab

### A marketplace platform connecting influencers and businesses through structured advertisement services.

------------------------------------------------------------------------

## Overview

AsanTab is a marketplace platform designed for influencer-based
advertising.

The platform allows influencers to create professional profiles,
showcase their advertising services, define pricing, and make their
social media reach available for businesses and users looking for
promotional opportunities.

The core idea is simple:

-   An influencer creates a profile
-   Adds available advertising services
-   Defines pricing and service details
-   Customers discover and purchase advertising opportunities

The platform focuses on creating a structured marketplace around
influencer advertising instead of relying on informal communication
channels.

------------------------------------------------------------------------

# Product Workflow

``` mermaid
flowchart LR
    A[Influencer] --> B[Create Profile]
    B --> C[Publish Advertising Services]
    C --> D[Marketplace Discovery]
    D --> E[Customer Purchase]
    E --> F[Order Management]
    F --> G[Notifications & Service Delivery]

    H[Admin Panel] --> B
    H --> C
    H --> F
```

------------------------------------------------------------------------

# Main Features

## User Management

-   Custom authentication system
-   Phone number based registration and login
-   Password-based authentication for users
-   Separate admin authentication workflow
-   User profile management

------------------------------------------------------------------------

## Influencer Marketplace

The main business module of AsanTab.

Features include:

-   Influencer profile creation
-   Social media presence management
-   Advertising service publishing
-   Service pricing management
-   Service categorization
-   Influencer discovery workflow

Example:

An influencer with:

-   1M Instagram followers
-   Active Telegram audience
-   Multiple social channels

can create advertising packages such as:

-   Instagram post advertisement
-   Story advertisement
-   Channel promotion

and allow customers to purchase these services.

------------------------------------------------------------------------

## Order Management System

The platform includes structured order workflows:

-   Service purchasing
-   Order tracking
-   Order-related data management
-   Customer and provider interaction flows
-   Order content management

------------------------------------------------------------------------

## Payment & Wallet Logic

Implemented business logic around:

-   User financial interactions
-   Wallet management
-   Order-related financial flows
-   Transaction-oriented structures

------------------------------------------------------------------------

## Notification System

The platform contains notification workflows for:

-   Email notifications
-   SMS notifications
-   User events
-   Order-related updates

Background processing is used for handling asynchronous tasks.

------------------------------------------------------------------------

## Content & Platform Management

Additional modules include:

-   Blog management
-   Reviews system
-   Ticketing system
-   Discount management
-   Search functionality
-   Statistics and analytics foundations
-   Location-based features

------------------------------------------------------------------------

# Backend Architecture

The project follows Django's MVT architecture with a modular application
structure.

``` mermaid
graph TD
    Client[User / Customer / Influencer]

    Client --> Django[Django Application]

    Django --> Accounts[Accounts]
    Django --> Services[Services]
    Django --> Orders[Orders]
    Django --> Wallet[Wallet]
    Django --> Notifications[Notifications]
    Django --> Search[Search]
    Django --> Reviews[Reviews]
    Django --> Blog[Blog]

    Django --> Core[Core Utilities]

    Core --> Cache[Cache Layer]
    Core --> Helpers[Shared Services]

    Django --> Database[(MySQL)]
```

------------------------------------------------------------------------

# Project Structure

    accounts        Authentication and user management
    services       Influencer advertising services
    orders         Purchase and order workflows
    wallet         Financial logic
    notifications  Communication workflows
    reviews        Rating and feedback system
    search         Platform search
    blog           Content management
    tickets        Support system
    discounts      Discount management
    locations      Location-based features
    stats          Analytics foundations
    core           Shared utilities and infrastructure helpers
    config         Global application configuration

------------------------------------------------------------------------

# Technical Highlights

-   Modular Django application design
-   Separation of business domains into independent apps
-   Service layer usage for reusable business logic
-   Custom authentication workflows
-   Background task handling
-   Cache integration
-   Structured order management
-   Reusable core utilities
-   Production-oriented project organization

------------------------------------------------------------------------

# Engineering Decisions

AsanTab was designed for a marketplace startup environment.

The architecture avoids unnecessary complexity while keeping enough
structure for future growth.

The goal was to build a system that is:

-   Maintainable
-   Extendable
-   Business-focused
-   Ready for additional marketplace features

------------------------------------------------------------------------

# Technology

Backend:

`Python` · `Django`

Database:

`MySQL`

Infrastructure:

`Linux` · `Git` · `Hosting Deployment`

Additional:

`Caching` · `Background Tasks` · `Email/SMS Integrations`

------------------------------------------------------------------------

# Project Scale

AsanTab contains multiple business domains implemented as separated
Django applications.

The system was built from the ground up, including:

-   Database modeling
-   Application architecture
-   Business logic
-   Authentication
-   Marketplace workflows
-   Administrative operations

------------------------------------------------------------------------

# Future Improvements

Potential future improvements:

-   Migration to PostgreSQL
-   Advanced caching strategies
-   Dedicated background workers
-   Containerized deployment
-   API-first architecture
-   Advanced search infrastructure

------------------------------------------------------------------------

# Author

Built and maintained by **Ali Dolat**

Backend Engineer focused on Django, scalable backend systems, and
production-oriented engineering.
