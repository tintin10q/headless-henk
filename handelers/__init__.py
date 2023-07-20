from .brand import handle_brand
from .stats import handle_get_stats
from .get_order import handle_get_order
from .get_capabilities import handle_get_capabilities
from .enable_capability import handle_enable_capability
from .disable_capability import handle_disable_capability
from .get_subscriptions import handle_get_subscriptions
from .subscribe import handle_subscribe
from .unsubscribe import handle_unsubscribe



# === Add colors.py to path ===
import sys
import os
# Assuming 'colors.py' is located in the same directory as 'side_package'
# If it's in a different location, provide the correct path accordingly.
colors_file_path = os.path.join(os.path.dirname(__file__), '../colors.py')

if colors_file_path not in sys.path:
    sys.path.insert(0, colors_file_path)