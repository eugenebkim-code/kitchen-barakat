import { translations } from './translations'
import { useLangStore } from '../stores/lang'

function lookup(dict, key) {
  let value = dict
  for (const part of key.split('.')) {
    value = value?.[part]
  }
  return value
}

export function useI18n() {
  const langStore = useLangStore()

  function t(key, vars = {}) {
    let value = lookup(translations[langStore.locale], key)
    if (value == null) {
      value = lookup(translations.ru, key)
    }
    if (typeof value !== 'string') {
      return key
    }
    return value.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? '')
  }

  return { t, langStore }
}

export function localizeField(obj, field, locale) {
  if (locale === 'ko') {
    return obj[`${field}_ko`] || obj[field]
  }
  return obj[field]
}
