# DomoticTuring
Simple and powerful script to control your pc and share stats to HomeAssistant.

## Idea

Start: load entities
Then: each Warehouse runs async; an entityManager that works async and will call periodically an async update for each entity.

Maybe each entity has its thread where it sleep and wakes up when it has to update