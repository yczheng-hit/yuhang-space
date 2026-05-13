import api from './index'

export const ordersApi = {
  addToCart(data) {
    return api.post('/orders', data)
  },

  listCarts() {
    return api.get('/orders/carts')
  },

  getCart(cartName = '默认购物车') {
    return api.get('/orders/cart', { params: { cart_name: cartName } })
  },

  updateOrder(id, data) {
    return api.patch(`/orders/${id}`, data)
  },

  deleteOrder(id) {
    return api.delete(`/orders/${id}`)
  },

  clearCart(cartName) {
    return api.delete(`/orders/cart/${encodeURIComponent(cartName)}`)
  },
}
