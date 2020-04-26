from typing import Tuple, Dict, Union, Any, Optional

t : Tuple[int, ...] = (1, 12, 234)
d : Dict[str, int] = {}

s : Union[int, str, Optional[bytes]] = None

f : bool = True

#print(reveal_type(t))