from app.domains.payment.domain.entity.coupon import Coupon
from app.domains.payment.infrastructure.orm.coupon_orm import CouponORM


class CouponMapper:
    @staticmethod
    def to_orm(entity: Coupon) -> CouponORM:
        return CouponORM(
            id=entity.id,
            code=entity.code,
            status=entity.status,
            memo=entity.memo,
            created_at=entity.created_at,
            used_at=entity.used_at,
            used_by_user_id=entity.used_by_user_id,
            used_order_id=entity.used_order_id,
        )

    @staticmethod
    def to_entity(orm: CouponORM) -> Coupon:
        return Coupon(
            id=orm.id,
            code=orm.code,
            status=orm.status,
            memo=orm.memo,
            created_at=orm.created_at,
            used_at=orm.used_at,
            used_by_user_id=orm.used_by_user_id,
            used_order_id=orm.used_order_id,
        )
