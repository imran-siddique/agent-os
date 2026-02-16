"""Tests for the vouching & bonding engine and liability matrix."""

import pytest
from hypervisor.liability.vouching import VouchingEngine, VouchingError
from hypervisor.liability import LiabilityMatrix


class TestVouchingEngine:
    def setup_method(self):
        self.engine = VouchingEngine()
        self.session = "session:test-1"

    def test_basic_vouch(self):
        record = self.engine.vouch(
            voucher_did="did:mesh:high",
            vouchee_did="did:mesh:low",
            session_id=self.session,
            voucher_sigma=0.8,
        )
        assert record.voucher_did == "did:mesh:high"
        assert record.vouchee_did == "did:mesh:low"
        assert record.is_active
        assert record.bonded_sigma_pct == 0.20
        assert abs(record.bonded_amount - 0.16) < 1e-9  # 0.8 * 0.20

    def test_cannot_vouch_for_self(self):
        with pytest.raises(VouchingError, match="Cannot vouch for yourself"):
            self.engine.vouch("did:mesh:a", "did:mesh:a", self.session, 0.8)

    def test_low_score_cannot_vouch(self):
        with pytest.raises(VouchingError, match="below minimum"):
            self.engine.vouch("did:mesh:low", "did:mesh:other", self.session, 0.3)

    def test_circular_vouching_rejected(self):
        self.engine.vouch("did:mesh:a", "did:mesh:b", self.session, 0.8)
        with pytest.raises(VouchingError, match="Circular"):
            self.engine.vouch("did:mesh:b", "did:mesh:a", self.session, 0.7)

    def test_sigma_eff_formula(self):
        """σ_eff = σ_L + (ω × σ_H_bonded)"""
        self.engine.vouch("did:mesh:high", "did:mesh:low", self.session, 0.9, bond_pct=0.5)
        # bonded_amount = 0.9 * 0.5 = 0.45
        # σ_eff = 0.3 + (0.2 * 0.45) = 0.3 + 0.09 = 0.39
        sigma_eff = self.engine.compute_sigma_eff(
            vouchee_did="did:mesh:low",
            session_id=self.session,
            vouchee_sigma=0.3,
            risk_weight=0.2,
        )
        assert abs(sigma_eff - 0.39) < 1e-9

    def test_sigma_eff_capped_at_1(self):
        self.engine.vouch("did:mesh:high", "did:mesh:low", self.session, 0.9, bond_pct=1.0)
        sigma_eff = self.engine.compute_sigma_eff(
            "did:mesh:low", self.session, 0.8, risk_weight=1.0
        )
        assert sigma_eff <= 1.0

    def test_multiple_vouchers(self):
        self.engine.vouch("did:mesh:a", "did:mesh:low", self.session, 0.8, bond_pct=0.5)
        self.engine.vouch("did:mesh:b", "did:mesh:low", self.session, 0.6, bond_pct=0.5)
        # bonded: 0.4 + 0.3 = 0.7
        # σ_eff = 0.1 + (0.5 * 0.7) = 0.1 + 0.35 = 0.45
        sigma_eff = self.engine.compute_sigma_eff(
            "did:mesh:low", self.session, 0.1, risk_weight=0.5
        )
        assert abs(sigma_eff - 0.45) < 1e-9

    def test_release_session_bonds(self):
        self.engine.vouch("did:mesh:a", "did:mesh:b", self.session, 0.8)
        self.engine.vouch("did:mesh:a", "did:mesh:c", self.session, 0.8)
        count = self.engine.release_session_bonds(self.session)
        assert count == 2
        assert self.engine.get_vouchers_for("did:mesh:b", self.session) == []

    def test_total_exposure(self):
        self.engine.vouch("did:mesh:a", "did:mesh:b", self.session, 0.8, bond_pct=0.3)
        self.engine.vouch("did:mesh:a", "did:mesh:c", self.session, 0.8, bond_pct=0.2)
        exposure = self.engine.get_total_exposure("did:mesh:a", self.session)
        assert abs(exposure - 0.40) < 1e-9  # 0.24 + 0.16


class TestLiabilityMatrix:
    def setup_method(self):
        self.matrix = LiabilityMatrix("session:test-1")

    def test_add_and_query(self):
        self.matrix.add_edge("did:a", "did:b", 0.2, "v1")
        assert len(self.matrix.who_vouches_for("did:b")) == 1
        assert len(self.matrix.who_is_vouched_by("did:a")) == 1

    def test_total_exposure(self):
        self.matrix.add_edge("did:a", "did:b", 0.2, "v1")
        self.matrix.add_edge("did:a", "did:c", 0.3, "v2")
        assert abs(self.matrix.total_exposure("did:a") - 0.5) < 1e-9

    def test_cycle_detection(self):
        self.matrix.add_edge("did:a", "did:b", 0.2, "v1")
        self.matrix.add_edge("did:b", "did:a", 0.2, "v2")
        assert self.matrix.has_cycle()

    def test_no_cycle(self):
        self.matrix.add_edge("did:a", "did:b", 0.2, "v1")
        self.matrix.add_edge("did:b", "did:c", 0.2, "v2")
        assert not self.matrix.has_cycle()

    def test_clear_releases_all(self):
        self.matrix.add_edge("did:a", "did:b", 0.2, "v1")
        self.matrix.clear()
        assert len(self.matrix.edges) == 0
