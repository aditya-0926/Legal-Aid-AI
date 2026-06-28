import { Badge } from '../ui/Badge'
import { DOMAIN_LABELS } from '../../utils/constants'

export function DomainBadge({ domain, confidence }) {
  const info = DOMAIN_LABELS[domain] ?? DOMAIN_LABELS.general
  return (
    <Badge className={info.color}>
      {info.emoji} {info.label}
    </Badge>
  )
}
