

class STATES:
    READY           = 0
    FETCH_FOLLOWS   = 1
    FETCH_FOLLOWERS = 2
    FOLLOW_FOLLOWS  = 3
    FOLLOW_FOLLOWERS= 4
    UNFOLLOWING     = 5
    TRAINING        = 6
    ERROR           = 7
    DISCOVER_FS     = 8 # Discover follow sources
