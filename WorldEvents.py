# Dictionary of Subscribers to certain events
subscribers = {} #empty, will be added to when needed

# adds a subscriber to an event
def subscribe(event_name: str, func) -> None:
    """
    Registers a handler function to respond to a specific event.
    
    Creates event category if it doesn't exist. Prevents duplicate
    subscriptions of the same function to the same event.
    
    Args:
        event_name: String identifier for the event type
        func: Callable that accepts a dict parameter with event data
        
    Example:
        subscribe("disaster_start", injure_near_disaster)
    """
    
    #if an event doesn't exist and someone wants to subscribe to it, the event is created
    if event_name not in subscribers :
        subscribers[event_name] = []

    if func not in subscribers[event_name]:
        subscribers[event_name].append(func)

# posts an event (alerts all subscribers)
def post(event_name: str, data: dict) :
    """
    Broadcasts an event to all registered handler functions.
    
    Calls each subscribed function with the provided data dictionary.
    Silently ignores events with no subscribers to avoid cluttering
    the subscriber dictionary with unused events.
    
    Args:
        event_name: String identifier for the event type
        data: Dictionary containing event-specific information
        
    Example:
        post("civilian injured", {"agent": injured_civilian})
    """

    #if an event doesn't exist and someone wants to post it, nothing is done.
    #ensures our subscribers dict isn't full of unused events
    if event_name not in subscribers :
        return

    for func in subscribers[event_name] :
        func(data)