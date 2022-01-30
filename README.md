# DomoticTuring
Simple and powerful script to control your pc and share stats to HomeAssistant.

## Idea

Start: load entities
Then: each Warehouse runs async; an entityManager that works async and will call periodically an async update for each entity.

Maybe each entity has its thread where it sleep and wakes up when it has to update

Warning: all entity must add the Command sensors in Initialize or PostInitialize and not after, so the Warehouses can handle them at start time

### Configurator

For WHs, get each wh conf from whs list in conf.
With this configuration for the single Warehouse, with the WClassManager I get its class.
In the class there must be a static method that gets the configuration and Instantiate the warehouse using the configuration.
Then this method returns with WH to the configurator which will add the entities later...

