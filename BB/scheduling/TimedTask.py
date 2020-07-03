from datetime import datetime, timedelta
import inspect

"""
A fairly generic class that, at its core, tracks when a requested amount of time has passed.
Using an expiryFunction, a function call may be delayed by a given amount of time.
Using autoRescheduling, this class can also be used to easily schedule reoccurring tasks.
At least one of expiryTime or expiryDelta must be given.
If the task is set to autoReschedule, issueTime is updated to show the task's current rescheduling time.

@param issueTime -- The datetime when this task was created. Default: now
@param expiryTime -- The datetime when this task should expire. Default: None
@param expiryDelta -- The timedelta to add to issueTime, to find the expiryTime. Default: None
@param expiryFunction -- The function to call once expiryTime has been reached/surpassed. Default: None
@param expiryFunctionArgs -- The data to pass to the expiryFunction. There is no type requirement, but a dictionary is recommended as a close representation of KWArgs. Default: {}
@param autoReschedule -- Whether or not this task should automatically reschedule itself by the same timedelta. Default: False
"""
class TimedTask:
    def __init__(self, issueTime=None, expiryTime=None, expiryDelta=None, expiryFunction=None, expiryFunctionArgs={}, autoReschedule=False):
        # Ensure that at least one of expiryTime or expiryDelta is specified
        if expiryTime is None and expiryDelta is None:
            raise ValueError("No expiry time given, both expiryTime and expiryDelta are None")
        
        # Calculate issueTime as now if none is given
        self.issueTime = datetime.utcnow() if issueTime is None else issueTime
        # Calculate expiryTime as issueTime + expiryDelta if none is given
        self.expiryTime = self.issueTime + expiryDelta if expiryTime is None else expiryTime
        # Calculate expiryDelta as expiryTime - issueTime if none is given. This is needed for rescheduling.
        self.expiryDelta = self.expiryTime - self.issueTime if expiryDelta is None else expiryDelta

        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}
        self.autoReschedule = autoReschedule

        # A task's 'gravestone' is marked as True when the TimedTask will no longer execute and can be removed from any TimedTask heap.
        # I.e, it is expired (whether manually or through timeout) and does not auto-reschedule.
        self.gravestone = False

        # Track whether or not the expiryFunction is a coroutine and needs to be awaited
        self.asyncExpiryFunction = inspect.iscoroutinefunction(expiryFunction)


    """
    < Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is < other's expiryTime, False otherwise. 
    """
    def __lt__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("< error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime < other.expiryTime


    """
    > Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is > other's expiryTime, False otherwise. 
    """
    def __gt__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("> error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime > other.expiryTime


    """
    <= Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is <= other's expiryTime, False otherwise. 
    """
    def __lte__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("<= error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime <= other.expiryTime


    """
    >= Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is >= other's expiryTime, False otherwise. 
    """
    def __gte__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError(">= error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime >= other.expiryTime

    
    """
    Decide whether or not this task has expired.
    This can be due to reaching the task's expiryTime, or due to manual expiry.

    @return -- True if this timedTask has been manually expired, or has reached its expiryTime. False otherwise
    """
    def isExpired(self):
        self.gravestone = self.gravestone or self.expiryTime <= datetime.utcnow()
        return self.gravestone


    """
    Call the task's expiryFunction, if one is specified.
    Handles passing of arguments to the expiryFunction, if specified.

    @return -- the results of the expiryFunction
    """
    async def callExpiryFunction(self):
        if self.asyncExpiryFunction:
            if self.hasExpiryFunctionArgs:
                return await self.expiryFunction(self.expiryFunctionArgs)
            else:
                return await self.expiryFunction()
        else:
            if self.hasExpiryFunctionArgs:
                return self.expiryFunction(self.expiryFunctionArgs)
            else:
                return self.expiryFunction()


    """
    Function to be called regularly, that handles the expiry of this task.
    Handles calling of the task's expiry function if specified, and rescheduling of the task if specified.

    @param callExpiryFunc -- Whether or not to call this task's expiryFunction if it is expired. Default: True
    @return -- True if this task is expired in this check, False otherwise. Regardless of autorescheduling.
    """
    async def doExpiryCheck(self, callExpiryFunc=True):
        expired = self.isExpired()
        # If the task has expired, call expiry function and reschedule if specified
        if expired:
            if callExpiryFunc and self.hasExpiryFunction:
                await self.callExpiryFunction()
            if self.autoReschedule:
                await self.reschedule()
        return expired

    
    """
    Reschedule this task, with the timedelta given/calculated on the task's creation, or to a given expiryTime/Delta.
    Rescheduling will update the task's issueTime to now. TODO: A firstIssueTime may be useful in the future to represent creation time.
    Giving an expiryTime or expiryDelta will not update the task's stored expiryDelta. I.e, if the task is rescheduled again without giving an expiryDelta,
    The expiryDelta given/calculated on the task's creation will be used.
    If both an expiryTime and an expiryDelta is given, the expiryTime takes precedence.

    @param expiryTime -- The new expiry time for the task. Default: now + expiryTime if expiryTime is specified, now + self.expiryTime otherwise
    @param expiryDelta -- The amount of time to wait until the task's next expiry. Default: now + self.expiryTime
    """
    async def reschedule(self, expiryTime=None, expiryDelta=None):
        # Update the task's issueTime to now
        self.issueTime = datetime.utcnow()
        # Create the new expiryTime from now + expirydelta
        self.expiryTime = self.issueTime + (self.expiryDelta if expiryDelta is None else expiryDelta) if expiryTime is None else expiryTime
        # reset the gravestone to False, in case the task had been expired and marked for removal
        self.gravestone = False


    """
    Force the expiry of this task.
    Handles calling of this task's expiryFunction, and rescheduling if specified. Set's the task's expiryTime to now.

    @param callExpiryFunction -- Whether or not to call the task's expiryFunction if the task expires. Default: True
    @return -- The result of the expiry function, if it is called
    """
    async def forceExpire(self, callExpiryFunc=True):
        # Update expiryTime
        self.expiryTime = datetime.utcnow()
        # Call expiryFunction and reschedule if specified
        if callExpiryFunc and self.hasExpiryFunction:
            expiryFuncResults = await self.callExpiryFunction()
        if self.autoReschedule:
            await self.reschedule()
        # Mark for removal if not rescheduled
        else:
            self.gravestone = True
        # Return expiry function results
        if callExpiryFunc and self.hasExpiryFunction:
            return expiryFuncResults


"""
A TimedTask which fetches the expiryDELTA (not time!) from a function, rather than actual arguments.
This allows for dynamically choosing the reschedule time.
If an expiryTime is specified, then this will be used for the first scheduling period. After this time is reached, the scheduler will switch to calling the delayTimeGenerator.

@param delayTimeGenerator -- Reference (not call!) to the function which generates the expiryDelta. Must return a timedelta.
@param delayTimeGeneratorArgs -- The data to pass to the delayTimeGenerator. There is no type requirement, but a dictionary is recommended as a close representation of KWArgs. Default: {}
@param issueTime -- The datetime when this task was created. Default: now
@param expiryTime -- The datetime when this task should expire. Default: None
@param expiryFunction -- The function to call once expiryTime has been reached/surpassed. Default: None
@param expiryFunctionArgs -- The data to pass to the expiryFunction. There is no type requirement, but a dictionary is recommended as a close representation of KWArgs. Default: {}
@param autoReschedule -- Whether or not this task should automatically reschedule itself. You probably want this to be True, otherwise you may as well use a TimedTask. Default: False
"""
class DynamicRescheduleTask(TimedTask):
    def __init__(self, delayTimeGenerator, delayTimeGeneratorArgs={}, issueTime=None, expiryTime=None, expiryFunction=None, expiryFunctionArgs={}, autoReschedule=False):
        # Initialise TimedTask-inherited attributes
        super(DynamicRescheduleTask, self).__init__(expiryDelta=delayTimeGenerator(delayTimeGeneratorArgs), issueTime=issueTime, expiryTime=expiryTime, expiryFunction=expiryFunction, expiryFunctionArgs=expiryFunctionArgs, autoReschedule=autoReschedule)
        self.delayTimeGenerator = delayTimeGenerator
        self.delayTimeGeneratorArgs = delayTimeGeneratorArgs
        self.hasDelayTimeGeneratorArgs = delayTimeGeneratorArgs != {}
        self.asyncDelayTimeGenerator = inspect.iscoroutinefunction(delayTimeGenerator)

    
    """
    Generate the next expiryTime using the delayTimeGenerator.

    @return -- The results of delayTimeGenerator. Should be a timedelta.
    """
    async def callDelayTimeGenerator(self):
        # await asynchronous delayTimeGenerators
        if self.asyncDelayTimeGenerator:
            # Pass args to delayTimeGenerator if specified
            if self.hasDelayTimeGeneratorArgs:
                return await self.delayTimeGenerator(self.delayTimeGeneratorArgs)
            else:
                return await self.delayTimeGenerator()
        # do not await synchronous delayTimeGenerators
        else:
            # Pass args to delayTimeGenerator if specified
            if self.hasDelayTimeGeneratorArgs:
                return self.delayTimeGenerator(self.delayTimeGeneratorArgs)
            else:
                return self.delayTimeGenerator()


    """
    @Override
    Start a new scheduling period for this task using the timedelta produced by delayTimeGenerator.
    
    """
    async def reschedule(self):
        # Update the task's issueTime to now
        self.issueTime = datetime.utcnow()
        # Create the new expiryTime from now + delayTimeGenerator result
        self.expiryTime = self.issueTime + await self.callDelayTimeGenerator()
        # reset the gravestone to False, in case the task had been expired and marked for removal
        self.gravestone = False