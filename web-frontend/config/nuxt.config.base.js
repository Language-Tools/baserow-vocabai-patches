import {
  featureFlagIsEnabled,
  getFeatureFlags,
} from '../modules/core/utils/env'

export default function (
  base = '@',
  premiumBase = '@/../premium/web-frontend',
  enterpriseBase = '@/../enterprise/web-frontend'
) {
  // Support adding in extra modules say from a plugin using the ADDITIONAL_MODULES
  // env variable which is a comma separated list of absolute module paths.
  const additionalModulesCsv = process.env.ADDITIONAL_MODULES
  const additionalModules = additionalModulesCsv
    ? additionalModulesCsv
        .split(',')
        .map((m) => m.trim())
        .filter((m) => m !== '')
    : []

  if (additionalModules.length > 0) {
    console.log(`Loading extra plugin modules: ${additionalModules}`)
  }
  const baseModules = [
    base + '/modules/core/module.js',
    base + '/modules/database/module.js',
  ]
  if (!process.env.BASEROW_OSS_ONLY) {
    baseModules.push(
      premiumBase + '/modules/baserow_premium/module.js',
      enterpriseBase + '/modules/baserow_enterprise/module.js'
    )
  }

  const featureFlags = getFeatureFlags()

  if (featureFlagIsEnabled(featureFlags, 'builder')) {
    baseModules.push(base + '/modules/builder/module.js')
  }

  const modules = baseModules.concat(additionalModules)
  return {
    modules,
    sentry: {
      dsn: 'https://33f709910b214ed282315bd91344bae0@o968582.ingest.sentry.io/6742673',
      config: {
      },
      publishRelease: {
        authToken: '9b89e612331511edbbd996b6a33f5072',
        org: 'language-tools',
        project: 'baserow-vocabai-frontend',
      }      
    },    
    build: {
      extend(config, ctx) {
        config.node = { fs: 'empty' }
      },
      babel: { compact: true },
      transpile: ['axios'],
    },
  }
}
