export default (client) => {
  return {
    fetchAll(pageId) {
      return client.get(`builder/page/${pageId}/elements/`)
    },
    create(pageId, elementType, beforeId = null, configuration = null) {
      const payload = {
        type: elementType,
        ...configuration,
      }

      if (beforeId !== null) {
        payload.before_id = beforeId
      }

      return client.post(`builder/page/${pageId}/elements/`, payload)
    },
    update(elementId, values) {
      return client.patch(`builder/element/${elementId}/`, values)
    },
    delete(elementId) {
      return client.delete(`builder/element/${elementId}/`)
    },
    move(elementId, beforeId) {
      return client.patch(`builder/element/${elementId}/move/`, {
        before_id: beforeId,
      })
    },
  }
}
