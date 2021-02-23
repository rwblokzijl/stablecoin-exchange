class BlockTypes:
    DESTRUCTION = b'eurotoken_destruction'
    CHECKPOINT  = b'eurotoken_checkpoint'
    CREATION    = b'eurotoken_creation'
    TRANSFER    = b'eurotoken_transfer'
    ROLLBACK    = b'eurotoken_rollback'

    EUROTOKEN_TYPES=[ CHECKPOINT, CREATION, DESTRUCTION, TRANSFER, ROLLBACK ]


