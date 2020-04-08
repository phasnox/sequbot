

class HiveError(Exception): pass
class HiveClusterEmpty(HiveError): pass
class HiveUnkownPath(HiveError): pass
class HiveConnectionError(HiveError): pass
class RobotBusy(HiveError): pass
