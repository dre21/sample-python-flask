

def validate_product_data(data, require_all=True):
    """
    Validates product fields from a request body dict.
    Returns (error_message, status_code) on failure, or (None, None) on success.
    require_all=True enforces name and price are present (use for POST).
    require_all=False allows partial updates (use for PUT).
    """
    name  = data.get('name')
    sku   = data.get('sku')
    price = data.get('price')
    stock_qty = data.get('stock_qty')


    if require_all and name is None:
        return "name is required", 400
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            return "name cannot be empty", 400
        if len(name.strip()) > 100:
            return "name cannot exceed 100 characters", 422

    if require_all and sku is None:
        return "sku is required", 400
    if sku is not None:
        if not isinstance(sku, str) or not sku.strip():
            return "sku cannot be empty", 400
        if len(sku.strip()) > 50:
            return "sku cannot exceed 50 characters", 422

    if require_all and price is None:
        return "price is required", 400
    if price is not None:
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            return "price must be a number", 400
        if price < 0:
            return "price must be 0 or greater", 422

    if stock_qty is not None:
        if not isinstance(stock_qty, int) or isinstance(stock_qty, bool):
            return "stock must be an integer", 400
        if stock_qty < 0:
            return "stock must be 0 or greater", 422

    return None, None