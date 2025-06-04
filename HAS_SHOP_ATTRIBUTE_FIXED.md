# 🔧 **FIXED: 'has_shop' Attribute Error**

## ✅ **Problem Solved!**

The game was crashing with:
```
AttributeError: 'InnkeeperNPC' object has no attribute 'has_shop'
```

### 🎯 **Root Cause**
The AI NPC classes (like `InnkeeperNPC`, `MasterMerchantNPC`, etc.) inherit from `BaseAINPC`, but `BaseAINPC` was missing the `has_shop` attribute that the game code expects all NPCs to have.

### 🔧 **Solution Applied**

#### 1. **Updated BaseAINPC Class**
Added shop attributes to `BaseAINPC` constructor:
```python
def __init__(self, x: int, y: int, name: str, dialog: Optional[List[str]] = None, 
             asset_loader=None, has_shop: bool = False, shop_items: Optional[List] = None, **kwargs):
    # ... existing code ...
    
    # Shop attributes (compatibility with regular NPC class)
    self.has_shop = has_shop
    self.shop_items = shop_items or []
    self.shop = None
    
    # Create shop if this NPC is a shopkeeper
    if self.has_shop:
        from ..ui.shop import Shop
        shop_name = f"{self.name}'s Shop"
        self.shop = Shop(shop_name, asset_loader)
```

#### 2. **Updated Shop-Enabled NPCs**
Fixed specific AI NPC classes to pass shop information to parent:

**Master Merchant NPC**:
```python
super().__init__(x, y, "Master Merchant", dialog=dialog, 
                asset_loader=asset_loader, has_shop=True, 
                shop_items=shop_items, **kwargs)
```

**Master Smith NPC**:
```python
super().__init__(x, y, "Master Smith", dialog=dialog, 
                asset_loader=asset_loader, has_shop=True,
                shop_items=shop_items, **kwargs)
```

**Innkeeper NPC**:
```python
super().__init__(x, y, "Innkeeper", dialog=dialog, 
                asset_loader=asset_loader, has_shop=True,
                shop_items=shop_items, **kwargs)
```

#### 3. **Added Shop Items**
Each shop-enabled NPC now has appropriate items:

- **Master Merchant**: Health Potions, Iron Sword, Leather Armor
- **Master Smith**: Steel Sword, Iron Shield, Chain Mail, Battle Axe  
- **Innkeeper**: Room for the Night, Hot Meal, Ale, Bread

### ✅ **What's Fixed**

1. ✅ **No more AttributeError**: All AI NPCs now have `has_shop` attribute
2. ✅ **Shop Integration**: NPCs with shops can be right-clicked to open shop
3. ✅ **MCP Tools**: NPCs can use `open_shop` MCP tool when appropriate
4. ✅ **Save/Load**: Shop attributes are properly saved and loaded

### 🎮 **Expected Behavior Now**

- **Right-click on Innkeeper**: Should work without crashing
- **AI Chat + Shop**: NPCs can use AI chat AND have functional shops
- **MCP Integration**: NPCs can use `open_shop` tool via MCP when players ask to trade

The game should now run without the AttributeError and NPCs should have both AI chat and shop functionality! 🎉