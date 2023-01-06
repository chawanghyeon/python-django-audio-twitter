export default {
  props: {
    filename  : { type: String, default: 'record'   },
    format    : { type: String, default: 'wav'      },
    headers   : { type: Object, default: () => ({}) },
    uploadUrl : { type: String                      }
  }
}
