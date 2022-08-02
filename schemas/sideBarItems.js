import {BellIcon} from '@sanity/icons'

export default {
  title: 'Sidebar Item',
  name: 'Description',
  type: 'document',
  icon: BellIcon,
  fields: [
    {
      title: 'Item Name',
      name: 'ItemName',
      type: 'string',
    },
    {
      title: 'Description',
      name: 'Description',
      type: 'string',
    }
  ],
  preview: {
    select: {
      title: 'ItemName',
      subtitle: 'Description',
    },
  },
}
