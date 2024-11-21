# Scryfall Full Card json Downloader

### Project to keep a local database updated with scryfall data.

### ToDo:
- [ ] Include Automation
- [ ] Add Async Capabilities
- [ ] Add logic that if database is there only update it. Rather than replace it.

### Current Workflow
- Download json file from scryfall api raw data page.
- Process json file into Dataframe
    - Process Prices and Images to explode lists
- Import to database