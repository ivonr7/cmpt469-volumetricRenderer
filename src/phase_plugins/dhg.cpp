#include <mitsuba/core/properties.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/phase.h>

NAMESPACE_BEGIN(mitsuba)
/*
    Isaac von Riedemann
    301423851
    imv@sfu.ca
*/
/**!

.. _phase-hg:

Double Henyey-Greenstein phase function (:monosp:`dhg`)
-----------------------------------------------

.. pluginparameters::

 * - g1
   - |float|
   - This parameter must be somewhere in the range -1 to 1
     (but not equal to -1 or 1). It denotes the *mean cosine* of scattering
     interactions. A value greater than zero indicates that medium interactions
     predominantly scatter incident light into a similar direction (i.e. the
     medium is *forward-scattering*), whereas values smaller than zero cause
     the medium to be scatter more light in the opposite direction.
   - |exposed|, |differentiable|, |discontinuous|
 * - g2
   - |float|
   - This parameter must be somewhere in the range -1 to 1
     (but not equal to -1 or 1). It denotes the *mean cosine* of scattering
     interactions. A value greater than zero indicates that medium interactions
     predominantly scatter incident light into a similar direction (i.e. the
     medium is *forward-scattering*), whereas values smaller than zero cause
     the medium to be scatter more light in the opposite direction.
   - |exposed|, |differentiable|, |discontinuous|
 * - f
   - |float|
   - This parameter must be somewhere in the range 0 to 1
     (but not equal to -1 or 1). It denotes the weighting between the two hg 
     functions
   - |exposed|, |differentiable|, |discontinuous|

.. tabs::
    .. code-tab:: xml

        <phase type="dhg">
            <float name="g1" value="0.1"/>
            <float name="g2" value="0.3"/>
            <float name="f" value="0.5"/>
        </phase>

    .. code-tab:: python

        'type': 'hg',
        'g': 0.1

*/
template <typename Float, typename Spectrum>
class DoubleHGPhaseFunction final : public PhaseFunction<Float, Spectrum> {
public:
    MI_IMPORT_BASE(PhaseFunction, m_flags, m_components)
    MI_IMPORT_TYPES(PhaseFunctionContext)

    DoubleHGPhaseFunction(const Properties &props) : Base(props) {
        ScalarFloat f = props.get<ScalarFloat>("f", 0.5f);
        ScalarFloat g1 = props.get<ScalarFloat>("g1", 0.8f);
        ScalarFloat g2 = props.get<ScalarFloat>("g2", 0.8f);
        ScalarFloat e = props.get<ScalarFloat>("eta", 0.5f);

        if ((g1 >= 1.f || g1 <= -1.f) && (g2 >= 1.f || g2 <= -1.f))
            Log(Error, "The asymmetry parameter must lie in the interval (-1, 1)!");
        f1 = f;
        m_g1 = g1;
        m_g2 = g2;
        eta = e;
        m_flags = +PhaseFunctionFlags::Anisotropic;
        m_components.push_back(m_flags); // TODO: check
    }

    void traverse(TraversalCallback *callback) override {
        callback->put_parameter("g1", m_g1, ParamFlags::Differentiable |
                                          ParamFlags::Discontinuous);
        callback->put_parameter("g2", m_g2, ParamFlags::Differentiable |
                                          ParamFlags::Discontinuous);
        callback->put_parameter("f", f1, ParamFlags::Differentiable |
        ParamFlags::Discontinuous); 
        callback->put_parameter("eta", eta, ParamFlags::Differentiable |
            ParamFlags::Discontinuous);                               
        }
    /// @brief extension of schlick computational speed up of hg function
    /// @param cos_theta 
    /// @return p(theta)
    MI_INLINE Float eval_dhg(Float cos_theta) const {
        Float num1 = f1 * (1 - dr::square(m_g1));
        Float num2 = (1-f1) * (1 - dr::square(m_g2));
        Float denom1 = (1+ dr::square(m_g1) - 2 * m_g1 * cos_theta);
        Float denom2 = (1+ dr::square(m_g2) - 2 * m_g2 * cos_theta);
        return num1 / denom1 + num2 / denom2;
    }

    std::tuple<Vector3f, Spectrum, Float> sample(const PhaseFunctionContext & /* ctx */,
                                                 const MediumInteraction3f &mi,
                                                 Float /* sample1 */,
                                                 const Point2f &sample2,
                                                 Mask active) const override {
        MI_MASKED_FUNCTION(ProfilerPhase::PhaseFunctionSample, active);
        Float g = (m_g1 + m_g2) / 2;
        Float sqr_term  = (1.f - dr::square(g)) / (1.f - g + 2.f * g * sample2.x()),
              cos_theta = (1.f + dr::square(g) - dr::square(sqr_term)) / (2.f * g);

        // Diffuse fallback
        dr::masked(cos_theta, dr::abs(g) < dr::Epsilon<ScalarFloat>) = 1.f - 2.f * sample2.x();

        Float sin_theta = dr::safe_sqrt(1.f - dr::square(cos_theta));
        auto [sin_phi, cos_phi] = dr::sincos(2.f * dr::Pi<ScalarFloat> * sample2.y());

        Vector3f wo = mi.to_world(
            Vector3f(sin_theta * cos_phi, sin_theta * sin_phi, -cos_theta));

        return { wo, 1.f, eval_dhg(-cos_theta) };
    }

    std::pair<Spectrum, Float> eval_pdf(const PhaseFunctionContext & /* ctx */,
                                        const MediumInteraction3f &mi,
                                        const Vector3f &wo,
                                        Mask active) const override {
        MI_MASKED_FUNCTION(ProfilerPhase::PhaseFunctionEvaluate, active);
        Float pdf = eval_dhg(dr::dot(wo, mi.wi));
        return { pdf, pdf };
    }

    std::string to_string() const override {
        std::ostringstream oss;
        oss << "DoubleHGPhaseFunction[" << std::endl
            << "  g = " << string::indent(m_g1) << std::endl
            << "]";
        return oss.str();
    }

    MI_DECLARE_CLASS()
private:
    Float m_g1,m_g2,f1,eta;
};

MI_IMPLEMENT_CLASS_VARIANT(DoubleHGPhaseFunction, PhaseFunction)
MI_EXPORT_PLUGIN(DoubleHGPhaseFunction, "Double Henyey-Greenstein phase function")
NAMESPACE_END(mitsuba)
