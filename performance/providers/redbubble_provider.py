class RedbubbleProvider:
    name = "REDBUBBLE_MANUAL_OR_OFFICIAL_EXPORT_ONLY"
    official = False
    read_only = True

    def fetch(self, *args, **kwargs):
        raise RuntimeError("REVIEW: Redbubble account automation is disabled until an approved official integration is verified. Use manual/official export ingestion.")
