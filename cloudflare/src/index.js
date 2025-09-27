import { Container, getRandom } from "@cloudflare/containers"
import { env } from "cloudflare:workers"

export class Backend extends Container {
  defaultPort = 8080
  sleepAfter = "1h"
  envVars = {
    CONFIG_PATH: env.CONFIG_PATH,
    ALLOWED_ORIGINS: env.ALLOWED_ORIGINS,
    R2_ACCESS_KEY_ID: env.R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY: env.R2_SECRET_ACCESS_KEY,
  }
}

const INSTANCE_COUNT = 3;

export default {
  async fetch(request, env, ctx) {
    const inst = await getRandom(env.BACKEND, INSTANCE_COUNT);

    for (const k of ["R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY"]) {
      if (!env[k]) return new Response(`Worker env missing: ${k}`, {status: 500})
    }

    try {
      const res = await inst.fetch(request)
      return res
    } catch (err) {
      const msg = `Container fetch failed: ${err?.message || err}`
      console.error(msg)
      return new Response(msg, { status: 503 })
    }
  },
}
